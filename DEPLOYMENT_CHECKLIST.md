# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Code & Configuration
- [ ] All code changes committed and pushed to repository
- [ ] All tests pass (if you have any)
- [ ] No console errors or warnings in development
- [ ] Database migrations are up to date
- [ ] `.env` files are NOT committed (check `.gitignore`)

### Environment Variables

#### Python Backend
- [ ] `DATABASE_URL` - Production PostgreSQL connection string
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `DATA_RAW_PATH` - Path to PDF files on production server
- [ ] `DATA_PROCESSED_PATH` - Path for processed data
- [ ] `EVAL_TESTSET_PATH` - Path to evaluation dataset (if used)
- [ ] `ALLOWED_ORIGINS` - Your production domains (comma-separated)

#### Next.js API Gateway
- [ ] `PYTHON_API_URL` - Your Python backend URL (e.g., `https://backend.yourdomain.com`)
- [ ] `ALLOWED_ORIGINS` - Your frontend domain(s) that can call the API

#### Next.js Frontend
- [ ] `NEXT_PUBLIC_API_URL` - Your API Gateway URL (e.g., `https://api.yourdomain.com`)

### Database
- [ ] PostgreSQL instance is running
- [ ] `vector` extension is enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Database has been populated with documents (via ingestion on first startup)
- [ ] Database credentials are secure (strong passwords)

### Data Files
- [ ] PDF files are uploaded to `DATA_RAW_PATH` on production server
- [ ] Paths are correctly configured for production filesystem

### Security
- [ ] `ALLOWED_ORIGINS` is set in both API Gateway and Python Backend
- [ ] No API keys or secrets are hardcoded in the code
- [ ] HTTPS is enabled on all services
- [ ] Database passwords are strong and secure

## Deployment Steps

### 1. Python Backend
- [ ] Deploy to Railway/Render/Fly.io or your hosting platform
- [ ] Set all environment variables in platform dashboard
- [ ] Verify backend is accessible at expected URL
- [ ] Check logs for any startup errors
- [ ] Verify document ingestion completes successfully

### 2. Next.js API Gateway
- [ ] Deploy to Vercel/Netlify or your hosting platform
- [ ] Set `PYTHON_API_URL` and `ALLOWED_ORIGINS` environment variables
- [ ] Verify API Gateway health endpoint works: `https://api.yourdomain.com/api/health`
- [ ] Test API Gateway can reach Python backend

### 3. Next.js Frontend
- [ ] Deploy to Vercel/Netlify or your hosting platform
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable
- [ ] Verify frontend loads without errors
- [ ] Check browser console for any errors

## Post-Deployment Testing

### Functionality Tests
- [ ] Frontend loads successfully
- [ ] Can send a chat message
- [ ] Chat responses are returned correctly
- [ ] Can create a new chat
- [ ] Can delete a chat
- [ ] Session management works correctly

### Integration Tests
- [ ] Frontend → API Gateway communication works
- [ ] API Gateway → Python Backend communication works
- [ ] Python Backend → PostgreSQL connection works
- [ ] Vector search returns relevant documents
- [ ] LLM responses are generated correctly

### Security Tests
- [ ] CORS is configured correctly (no CORS errors in browser console)
- [ ] Requests from unauthorized origins are blocked
- [ ] API endpoints validate input correctly
- [ ] Error messages don't leak sensitive information

### Performance Tests
- [ ] Response times are acceptable (< 5 seconds for chat)
- [ ] No memory leaks or resource issues
- [ ] Database queries are optimized

## Monitoring & Maintenance

- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Set up application logging
- [ ] Set up uptime monitoring
- [ ] Document deployment process for your team
- [ ] Set up automated backups for database
- [ ] Plan for scaling if needed

## Rollback Plan

- [ ] Know how to revert to previous deployment
- [ ] Keep previous deployment artifacts
- [ ] Test rollback process in staging first

## Important Notes

1. **Never commit `.env` files** - Use platform environment variables
2. **Use HTTPS everywhere** - All services must use HTTPS in production
3. **Test CORS thoroughly** - Incorrect CORS config will break your app
4. **Monitor API costs** - Groq API usage can add up
5. **Backup your database** - Especially after document ingestion
6. **Document your deployment** - For future reference

---

**Last Updated**: 2024
**Documentation**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions

