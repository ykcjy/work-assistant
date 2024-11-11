import React, { useState, useRef, useEffect } from 'react';
import { Button, message, Space, Table } from 'antd';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons';
import AddBookmarkDialog from './AddBookmarkDialog';

function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([]);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  // 加载书签列表
  const loadBookmarks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/bookmarks');
      const data = await response.json();
      setBookmarks(data);
    } catch (error) {
      message.error('加载书签失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加书签
  const addBookmark = async (bookmark) => {
    try {
      const response = await fetch('/api/bookmarks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookmark),
      });
      if (!response.ok) throw new Error('添加失败');
      await loadBookmarks();
      return true;
    } catch (error) {
      message.error('添加书签失败');
      return false;
    }
  };

  const handleImportClick = () => {
    fileInputRef.current.click();
  };

  const handleFileImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      const bookmarks = lines.map(line => {
        const [category, title, url, username, defaultBrowser] = line.split(',').map(item => item.trim());
        return {
          category,
          title,
          url,
          username,
          defaultBrowser
        };
      });

      const response = await fetch('/api/bookmarks/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ bookmarks })
      });

      if (!response.ok) {
        throw new Error('导入失败');
      }

      const result = await response.json();
      message.success(`成功导入 ${result.count} 个网址`);
      loadBookmarks();
    } catch (error) {
      message.error('导入失败: ' + error.message);
    }
    
    event.target.value = '';
  };

  useEffect(() => {
    loadBookmarks();
  }, []);

  const columns = [
    {
      title: '名称',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '网址',
      dataIndex: 'url',
      key: 'url',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    // 其他列...
  ];

  return (
    <div>
      <div className="nav-bar">
        <div className="nav-links">
          <a href="/bookmarks">网址管理</a>
          <a href="/files">文件管理</a>
          <a href="/tasks">待办任务</a>
          <a href="/self-tasks">已办任务</a>
          <a href="/holidays">节假日管理</a>
        </div>
      </div>

      <div className="sub-nav">
        <div className="left-buttons">
          <a href="/add-bookmark">添加书签</a>
          <a href="/edit-bookmark">编辑书签</a>
          <a href="/delete-bookmark">删除书签</a>
          <a href="#" onClick={(e) => {
            e.preventDefault();
            handleImportClick();
          }}>批量导入</a>
        </div>
        <div className="right-buttons">
          <a href="/add-category">添加分类</a>
          <a href="/edit-category">编辑分类</a>
          <a href="/delete-category">删除分类</a>
        </div>
      </div>

      <Table 
        dataSource={bookmarks}
        columns={columns}
        loading={loading}
        rowKey="id"
      />

      {showAddDialog && (
        <AddBookmarkDialog
          visible={showAddDialog}
          onClose={() => setShowAddDialog(false)}
          onAdd={addBookmark}
        />
      )}

      <input 
        type="file" 
        accept=".txt,.csv"
        style={{ display: 'none' }}
        ref={fileInputRef}
        onChange={handleFileImport}
      />
    </div>
  );
}

export default Bookmarks;