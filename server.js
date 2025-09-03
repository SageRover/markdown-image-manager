const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const multer = require('multer');
const chokidar = require('chokidar');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public')); // 用于托管前端文件

// 配置部分
const CONFIG = {
  imageExtensions: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'],
  mappingFile: 'image-mapping.json',
  picListPath: 'piclist', // 或完整路径，如 '/usr/local/bin/piclist'
  defaultUploadCommand: 'upload' // PicList的上传命令
};

// 全局变量
let imageMapping = {};
let currentScanResults = {
  mdFiles: 0,
  images: 0,
  references: 0,
  invalidRefs: [],
  unusedImages: []
};

// 加载图片映射表
function loadMapping() {
  try {
    if (fs.existsSync(CONFIG.mappingFile)) {
      imageMapping = JSON.parse(fs.readFileSync(CONFIG.mappingFile, 'utf8'));
      console.log('图片映射表加载成功');
    }
  } catch (error) {
    console.warn(`无法加载映射文件: ${error.message}`);
    imageMapping = {};
  }
}

// 保存图片映射表
function saveMapping() {
  try {
    fs.writeFileSync(CONFIG.mappingFile, JSON.stringify(imageMapping, null, 2));
    console.log(`映射表已保存到 ${CONFIG.mappingFile}`);
    return true;
  } catch (error) {
    console.error(`保存映射表失败: ${error.message}`);
    return false;
  }
}

// 扫描文件夹中的所有文件和图片
function scanDirectory(dirPath) {
  const files = [];
  const images = [];
  
  function traverse(currentPath) {
    const items = fs.readdirSync(currentPath);
    
    for (const item of items) {
      const fullPath = path.join(currentPath, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        traverse(fullPath);
      } else {
        const ext = path.extname(item).toLowerCase();
        if (item.endsWith('.md')) {
          files.push(fullPath);
        } else if (CONFIG.imageExtensions.includes(ext)) {
          images.push(fullPath);
        }
      }
    }
  }
  
  try {
    traverse(dirPath);
    return { files, images };
  } catch (error) {
    console.error(`扫描目录时出错: ${error.message}`);
    return { files: [], images: [] };
  }
}

// 从Markdown文件中提取图片引用
function extractImageReferences(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    // 匹配Markdown图片语法 ![alt](src)
    const mdRegex = /!\[.*?\]\((.*?)\)/g;
    // 匹配HTML图片标签 <img src="...">
    const htmlRegex = /<img[^>]+src="([^">]+)"/g;
    
    const references = [];
    let match;
    
    while ((match = mdRegex.exec(content)) !== null) {
      references.push(match[1]);
    }
    
    while ((match = htmlRegex.exec(content)) !== null) {
      references.push(match[1]);
    }
    
    return references;
  } catch (error) {
    console.error(`读取文件失败: ${filePath}`, error.message);
    return [];
  }
}

// API路由

// 获取当前状态
app.get('/api/status', (req, res) => {
  res.json({
    mappingCount: Object.keys(imageMapping).length,
    ...currentScanResults
  });
});

// 扫描目录
app.post('/api/scan', (req, res) => {
  const { directory } = req.body;
  if (!directory) {
    return res.status(400).json({ error: '目录路径不能为空' });
  }
  
  try {
    console.log(`开始扫描目录: ${directory}`);
    const { files, images } = scanDirectory(directory);
    
    const allImageRefs = [];
    const unusedImages = new Set(images);
    const invalidRefs = [];
    
    // 分析每个Markdown文件
    for (const file of files) {
      const refs = extractImageReferences(file);
      for (const ref of refs) {
        allImageRefs.push({ file, ref });
        
        // 检查引用是否有效
        let imagePath;
        if (path.isAbsolute(ref)) {
          imagePath = ref;
        } else {
          imagePath = path.resolve(path.dirname(file), ref);
        }
        
        if (!fs.existsSync(imagePath)) {
          invalidRefs.push({ file, ref });
        } else {
          // 从未使用列表中移除
          unusedImages.delete(imagePath);
        }
      }
    }
    
    // 更新当前扫描结果
    currentScanResults = {
      mdFiles: files.length,
      images: images.length,
      references: allImageRefs.length,
      invalidRefs,
      unusedImages: Array.from(unusedImages)
    };
    
    res.json(currentScanResults);
  } catch (error) {
    console.error('扫描失败:', error);
    res.status(500).json({ error: `扫描失败: ${error.message}` });
  }
});

// 获取Markdown文件列表
app.get('/api/md-files', (req, res) => {
  const { directory } = req.query;
  if (!directory) {
    return res.status(400).json({ error: '目录路径不能为空' });
  }
  
  try {
    const { files } = scanDirectory(directory);
    // 只返回相对路径
    const relativeFiles = files.map(file => path.relative(directory, file));
    res.json(relativeFiles);
  } catch (error) {
    console.error('获取文件列表失败:', error);
    res.status(500).json({ error: `获取文件列表失败: ${error.message}` });
  }
});

// 上传图片到图床
app.post('/api/upload', (req, res) => {
  const { mdFile, directory } = req.body;
  if (!mdFile || !directory) {
    return res.status(400).json({ error: '参数不完整' });
  }
  
  const fullMdPath = path.join(directory, mdFile);
  if (!fs.existsSync(fullMdPath)) {
    return res.status(404).json({ error: 'Markdown文件不存在' });
  }
  
  try {
    console.log(`处理文件: ${fullMdPath}`);
    const refs = extractImageReferences(fullMdPath);
    const uploadResults = [];
    
    for (const ref of refs) {
      let imagePath;
      if (path.isAbsolute(ref)) {
        imagePath = ref;
      } else {
        imagePath = path.resolve(path.dirname(fullMdPath), ref);
      }
      
      // 检查图片是否存在
      if (!fs.existsSync(imagePath)) {
        uploadResults.push({
          imagePath,
          success: false,
          message: `图片不存在: ${imagePath}`
        });
        continue;
      }
      
      // 如果已经上传过，跳过
      if (imageMapping[imagePath]) {
        uploadResults.push({
          imagePath,
          success: true,
          message: '已上传过',
          url: imageMapping[imagePath]
        });
        continue;
      }
      
      try {
        console.log(`上传: ${imagePath}`);
        // 使用PicList上传图片
        const result = execSync(`${CONFIG.picListPath} ${CONFIG.defaultUploadCommand} "${imagePath}"`).toString().trim();
        
        // 假设PicList返回URL
        const url = result;
        imageMapping[imagePath] = url;
        uploadResults.push({
          imagePath,
          success: true,
          message: '上传成功',
          url
        });
      } catch (error) {
        uploadResults.push({
          imagePath,
          success: false,
          message: `上传失败: ${error.message}`
        });
      }
    }
    
    // 保存映射表
    saveMapping();
    
    res.json({
      success: true,
      results: uploadResults
    });
  } catch (error) {
    console.error('上传失败:', error);
    res.status(500).json({ error: `上传失败: ${error.message}` });
  }
});

// 替换图片链接
app.post('/api/replace', (req, res) => {
  const { mdFile, directory, linkType } = req.body;
  if (!mdFile || !directory) {
    return res.status(400).json({ error: '参数不完整' });
  }
  
  const fullMdPath = path.join(directory, mdFile);
  if (!fs.existsSync(fullMdPath)) {
    return res.status(404).json({ error: 'Markdown文件不存在' });
  }
  
  try {
    let content = fs.readFileSync(fullMdPath, 'utf8');
    const refs = extractImageReferences(fullMdPath);
    let replaced = 0;
    
    for (const ref of refs) {
      let imagePath;
      if (path.isAbsolute(ref)) {
        imagePath = ref;
      } else {
        imagePath = path.resolve(path.dirname(fullMdPath), ref);
      }
      
      let replacement;
      if (linkType === 'remote') {
        // 替换为远程URL
        if (imageMapping[imagePath]) {
          replacement = imageMapping[imagePath];
        } else {
          console.warn(`没有找到映射: ${imagePath}`);
          continue;
        }
      } else {
        // 替换为本地路径（相对路径）
        replacement = path.relative(path.dirname(fullMdPath), imagePath);
      }
      
      // 转义特殊字符用于正则表达式
      const escapedRef = ref.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(escapedRef, 'g');
      content = content.replace(regex, replacement);
      replaced++;
    }
    
    // 备份原文件
    const backupPath = fullMdPath + '.bak';
    fs.copyFileSync(fullMdPath, backupPath);
    
    // 写入新内容
    fs.writeFileSync(fullMdPath, content, 'utf8');
    
    res.json({
      success: true,
      replaced,
      backupPath
    });
  } catch (error) {
    console.error('替换失败:', error);
    res.status(500).json({ error: `替换失败: ${error.message}` });
  }
});

// 清理未使用的图片
app.post('/api/cleanup', (req, res) => {
  const { directory } = req.body;
  if (!directory) {
    return res.status(400).json({ error: '目录路径不能为空' });
  }
  
  try {
    // 重新扫描以确保数据最新
    const { files, images } = scanDirectory(directory);
    
    const unusedImages = new Set(images);
    
    // 分析每个Markdown文件
    for (const file of files) {
      const refs = extractImageReferences(file);
      for (const ref of refs) {
        // 检查引用是否有效
        let imagePath;
        if (path.isAbsolute(ref)) {
          imagePath = ref;
        } else {
          imagePath = path.resolve(path.dirname(file), ref);
        }
        
        if (fs.existsSync(imagePath)) {
          // 从未使用列表中移除
          unusedImages.delete(imagePath);
        }
      }
    }
    
    const unusedImagesArray = Array.from(unusedImages);
    let deletedCount = 0;
    let mappingUpdated = false;
    
    for (const imagePath of unusedImagesArray) {
      try {
        fs.unlinkSync(imagePath);
        console.log(`已删除: ${imagePath}`);
        deletedCount++;
        
        // 从映射中移除
        if (imageMapping[imagePath]) {
          delete imageMapping[imagePath];
          mappingUpdated = true;
        }
      } catch (error) {
        console.error(`删除失败: ${imagePath}`, error.message);
      }
    }
    
    if (mappingUpdated) {
      saveMapping();
    }
    
    // 更新扫描结果
    currentScanResults.unusedImages = currentScanResults.unusedImages.filter(
      img => !unusedImagesArray.includes(img)
    );
    
    res.json({
      success: true,
      deletedCount,
      total: unusedImagesArray.length
    });
  } catch (error) {
    console.error('清理失败:', error);
    res.status(500).json({ error: `清理失败: ${error.message}` });
  }
});

// 获取映射表
app.get('/api/mapping', (req, res) => {
  res.json(imageMapping);
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
  // 加载映射表
  loadMapping();
});