# N2S TMMi Tracker - Version Changelog
## Version 1.1.0 (2025-08-04)
**Major Feature Release: Database Persistence & Rebranding**

### ✨ New Features
- **Complete rebrand** from "TMMi Assessment Tracker" to "N2S TMMi Tracker"
- **Database persistence system** with environment-based configuration
- **Database Administration interface** with backup/restore capabilities
- **Docker deployment** support with persistent volumes
- **GitHub Actions CI/CD** pipeline with automated health checks
- **Automatic database backups** before deployments

### 🏗️ Infrastructure
- Added Dockerfile and docker-compose.yml for containerization
- Enhanced startup script with environment variable support
- Comprehensive deployment documentation
- Database health monitoring and integrity checks

### 📝 Documentation
- `deploy.md` - Production deployment guide
- `PERSISTENCE_SUMMARY.md` - Implementation overview
- Updated README with new branding

### 🔧 Technical Improvements
- Environment-configurable database paths (`TMMI_DB_PATH`, `TMMI_BACKUP_DIR`)
- Database statistics and maintenance tools
- Improved error handling and logging
- Production-ready configuration

---
## Version 1.0.0 (Previous)
**Initial Release**
- Basic TMMi assessment functionality
- Organization management
- Progress tracking
- Assessment history
- Dashboard analytics

---
## Version Management

To update version for next release:

1. **Update version in `pyproject.toml`**:
   ```toml
   version = "X.Y.Z"
   ```
2. **Update this changelog** with new features

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "chore: bump version to vX.Y.Z"
   git push origin main
   ```
### Version Numbering
- **Major (X.0.0)**: Breaking changes, major feature overhauls
- **Minor (1.X.0)**: New features, significant improvements
- **Patch (1.1.X)**: Bug fixes, minor improvements