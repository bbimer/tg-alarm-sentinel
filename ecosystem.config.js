module.exports = {
  apps: [
    {
      name: 'tgalarm-monitor',
      script: 'monitor.py',
      interpreter: 'python3',
      restart_delay: 3000,
      autorestart: true,
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'tgalarm-adminbot',
      script: 'admin_bot.py',
      interpreter: 'python3',
      restart_delay: 3000,
      autorestart: true,
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
