# 🔒 Pre-Push Security Checklist

Before pushing to GitHub, verify these files are NOT in your repository:

## ❌ Files That Should NOT Be Committed

### Environment Files
- [ ] `.env`
- [ ] `.env.local`
- [ ] `.env.production`
- [ ] `.env.development`
- [ ] `backend/.env`
- [ ] `frontend/.env`

### Secrets & Credentials
- [ ] `secrets/` folder
- [ ] `firebase-adminsdk*.json`
- [ ] `gcp-service-account.json`
- [ ] `aws-credentials.json`
- [ ] Any `.pem`, `.key`, `.crt` files

### Dependencies (Large Files)
- [ ] `node_modules/` folder
- [ ] `venv/` folder
- [ ] `backend/venv/` folder
- [ ] `__pycache__/` folders

### Database & Cache Files
- [ ] `*.db`, `*.sqlite` files
- [ ] `postgres_data/` folder
- [ ] `redis_data/` folder
- [ ] `n8n_data/` folder

### Build Artifacts
- [ ] `frontend/dist/` folder
- [ ] `frontend/build/` folder
- [ ] `*.log` files
- [ ] `*.pyc` files

### ML Models (Large Files)
- [ ] `ml-models/*.pkl` files
- [ ] `training_data/*.csv` files (unless small examples)

---

## ✅ Files That SHOULD Be Committed

### Configuration Templates
- [x] `.env.example` files
- [x] `docker-compose.yml`
- [x] Dockerfiles

### Source Code
- [x] All `.py` files in `backend/app/`
- [x] All `.ts`, `.tsx` files in `frontend/src/`
- [x] `package.json`, `requirements.txt`

### Documentation
- [x] `README.md`
- [x] `GITHUB_DEPLOYMENT_GUIDE.md`
- [x] Any other `.md` documentation

### Git Configuration
- [x] `.gitignore`
- [x] `.github/` folder (if you have workflows)

---

## 🔍 How to Verify

Run this command to check what will be committed:

```powershell
cd C:\Users\Lenovo\Desktop\Intelli_Rate
git status
```

**Look for:**
- ❌ RED files = Not staged (won't be committed)
- ✅ GREEN files = Staged (will be committed)

---

## 🚨 If You See Sensitive Files

If `git status` shows files that should be ignored:

```powershell
# Remove specific file from staging
git rm --cached .env

# Remove entire folder from staging
git rm -r --cached secrets/

# Update .gitignore if needed, then:
git add .gitignore
git commit -m "Update .gitignore to exclude sensitive files"
```

---

## ✅ Final Verification

Before `git push`, run:

```powershell
# See what will be committed
git log --oneline -1

# See the actual changes
git diff HEAD~1 HEAD --name-only

# Make sure .env is NOT in the list!
```

---

## 🎯 Safe to Push?

If all checks pass:
- ✅ No `.env` files
- ✅ No `secrets/` folder
- ✅ No `node_modules/` or `venv/`
- ✅ No API keys or passwords in code

**Then you're ready to push!**

```powershell
git push -u origin main
```

---

## 🔐 Additional Security Tips

1. **Enable Secret Scanning on GitHub:**
   - Go to: Settings → Code security and analysis
   - Enable "Secret scanning"

2. **Review commits before pushing:**
   ```powershell
   git log -p -1  # Shows the last commit with changes
   ```

3. **Use .env.example files:**
   - Create template files without real values
   - Commit these as examples

4. **Never commit:**
   - API keys
   - Passwords
   - Private keys
   - Database credentials
   - OAuth tokens

---

**✅ Double-checked everything? Great! Now push to GitHub! 🚀**
