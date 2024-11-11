const express = require('express');
const router = express.Router();
const Bookmark = require('../models/Bookmark');

// 修改批量导入的处理函数
router.post('/import', async (req, res) => {
  try {
    const { bookmarks } = req.body;
    
    // 验证输入
    if (!Array.isArray(bookmarks)) {
      return res.status(400).json({ error: '无效的数据格式' });
    }
    
    // 验证必填字段
    const invalidBookmarks = bookmarks.filter(b => !b.url || !b.title);
    if (invalidBookmarks.length > 0) {
      return res.status(400).json({ error: '存在无效的书签数据' });
    }
    
    // 批量插入数据库
    const results = await Promise.all(
      bookmarks.map(bookmark => 
        Bookmark.create({
          category: bookmark.category || '默认分类',
          title: bookmark.title,
          url: bookmark.url,
          username: bookmark.username || '',
          defaultBrowser: bookmark.defaultBrowser || '',
          userId: req.user.id
        })
      )
    );
    
    res.json({ success: true, count: results.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 