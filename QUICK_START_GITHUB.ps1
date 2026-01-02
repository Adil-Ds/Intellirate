# =============================================================
# Quick Start: Push IntelliRate to GitHub
# =============================================================
# This script helps you quickly push your project to GitHub
# Run each command ONE BY ONE in PowerShell
# =============================================================

# STEP 1: Navigate to your project
cd C:\Users\Lenovo\Desktop\Intelli_Rate

# STEP 2: Configure Git (REPLACE WITH YOUR INFO!)
git config --global user.name "Your Name Here"
git config --global user.email "your.email@example.com"

# STEP 3: Initialize Git
git init

# STEP 4: Add all files
git add .

# STEP 5: Create first commit
git commit -m "Initial commit: IntelliRate API Gateway with ML analytics"

# STEP 6: Add GitHub remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/IntelliRate.git

# STEP 7: Rename branch to main
git branch -M main

# STEP 8: Push to GitHub
git push -u origin main

# =============================================================
# That's it! Your code is now on GitHub! 🎉
# =============================================================
