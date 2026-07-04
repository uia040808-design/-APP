// ============================================
// 晚秋记账 - Electron 主进程
// 负责创建桌面窗口并加载前端页面
// ============================================

const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: '晚秋记账',
    icon: path.join(__dirname, 'src', 'icon.png'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // 加载前端页面
  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  // 窗口关闭时释放资源
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Electron 初始化完成后创建窗口
app.whenReady().then(createWindow);

// 所有窗口关闭时退出应用（macOS 除外）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// macOS：点击 dock 图标时重新创建窗口
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
