# 测试修复逻辑

## 正常路径（应该能找到）
![正常图片](./images/test.png)

## 不存在的路径（应该找不到）
![不存在](./nonexistent/image.png)

## URL编码路径（应该通过解码找到）
![编码图片](images/%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87.png)

## 相对路径（应该能找到）
![相对路径](../markdown-image-manager/images/test.png)