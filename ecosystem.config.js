module.exports = {
  apps: [{
    name: 'horeca-backend',
    script: 'venv/bin/gunicorn',
    args: 'app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker',
    cwd: '/var/www/horeca/backend',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
