# 🎓 Viswam EduTech Online Exam - Hosting Guide

## Quick Start Options (Free & Easy)

### **Option 1: GitHub Pages (Recommended - FREE)**
Best for: Quick deployment, no backend needed

**Steps:**
1. Create GitHub account at github.com
2. Create new repository named: `viswam-edutech`
3. Upload `exam-proctoring-system.html` as `index.html`
4. Go to Settings → Pages → Select main branch
5. Your site will be at: `https://yourusername.github.io/viswam-edutech`

**Advantages:**
- ✅ Completely FREE
- ✅ Auto HTTPS
- ✅ Custom domain support
- ✅ No configuration needed
- ✅ Data stored locally (browser)

---

### **Option 2: Netlify (FREE - Easiest)**
Best for: Simplest setup, drag & drop

**Steps:**
1. Go to netlify.com
2. Click "Deploy manually"
3. Drag & drop `exam-proctoring-system.html`
4. Rename to `index.html` before uploading
5. Done! Your site is live instantly

**Your URL:** `https://your-site-name.netlify.app`

**Advantages:**
- ✅ Drag & drop deployment
- ✅ Auto HTTPS
- ✅ Fast & reliable
- ✅ Easy custom domain

---

### **Option 3: Vercel (FREE)**
Similar to Netlify

**Steps:**
1. Go to vercel.com
2. Import your GitHub repo or upload file
3. One-click deployment
4. Live instantly

---

### **Option 4: Firebase Hosting (FREE)**
Google's hosting platform

**Steps:**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize project
firebase init hosting

# Deploy
firebase deploy
```

**Advantages:**
- ✅ Google infrastructure
- ✅ Super fast
- ✅ Free tier very generous
- ✅ Custom domain support

---

## Paid Options (For Production)

### **Option 5: Web Hosting with cPanel**
Best for: Professional deployment, custom features

**Popular Providers:**
- Bluehost: $2.95/month
- HostGator: $3.95/month
- SiteGround: $2.99/month (first year)

**Features:**
- ✅ Email hosting
- ✅ More storage
- ✅ Better support
- ✅ Custom domains
- ✅ SSL certificates

**Setup:**
1. Buy hosting plan
2. Upload `exam-proctoring-system.html` via FTP/cPanel
3. Rename to `index.html`
4. Access via your domain

---

### **Option 6: Cloud Hosting (Scalable)**

#### **AWS (Amazon Web Services)**
```
- S3 + CloudFront: $1-5/month
- EC2 Instance: $5-20/month
```

#### **Google Cloud**
```
- Cloud Storage: Free tier available
- Compute Engine: $10-50/month
```

#### **Microsoft Azure**
```
- Static Web Apps: $20/month
- App Service: $15-100/month
```

---

## Step-by-Step: GitHub Pages (Easiest)

### **Complete Tutorial:**

1. **Create GitHub Account**
   - Go to github.com
   - Click "Sign up"
   - Fill details and verify email

2. **Create Repository**
   - Click "+" → "New repository"
   - Name: `viswam-edutech`
   - Description: "Online Exam Management System"
   - Choose "Public"
   - Click "Create repository"

3. **Upload File**
   - Click "Add file" → "Upload files"
   - Rename your file to `index.html`
   - Select the file: `exam-proctoring-system.html`
   - Drag & drop OR browse
   - Scroll down → Click "Commit changes"

4. **Enable GitHub Pages**
   - Go to "Settings"
   - Scroll to "Pages"
   - Under "Source" → Select "main" branch
   - Click "Save"
   - Wait 2-3 minutes
   - Your URL appears: `https://yourusername.github.io/viswam-edutech`

5. **Access Your Site**
   - Copy the URL
   - Open in browser
   - System is now LIVE!

---

## Step-by-Step: Netlify (Most User-Friendly)

1. **Visit Netlify**
   - Go to netlify.com
   - No signup needed initially

2. **Create index.html**
   - Save `exam-proctoring-system.html` as `index.html`

3. **Deploy**
   - Drag & drop `index.html` onto Netlify homepage
   - Wait 5 seconds
   - Your live URL appears instantly!

4. **Custom Domain (Optional)**
   - Go to Domain settings
   - Add your domain
   - Update DNS records
   - Website is now at your custom domain

---

## Important Notes for Data Persistence

⚠️ **Current System:**
- Uses **browser localStorage**
- Data saved locally on each device
- Different users = different data
- Cleared if browser cache is cleared

### **To Add Server-Side Database:**

You would need a backend (Node.js, Python, etc.) with database (MongoDB, PostgreSQL)

**Simple Backend Option:**
```javascript
// Use Firebase Realtime Database (FREE tier)
// Add to your HTML:
<script src="https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.0.0/firebase-database.js"></script>

// Then replace localStorage with Firebase calls
```

---

## Custom Domain Setup

### **After Hosting, Add Custom Domain:**

1. **Buy Domain**
   - Namecheap.com (~$5/year)
   - GoDaddy (~$12/year)
   - Google Domains (~$12/year)

2. **Point Domain to Host**
   - Get nameservers from your host
   - Go to domain registrar
   - Update nameservers
   - Wait 24-48 hours for propagation

3. **Add SSL (HTTPS)**
   - Most platforms include free SSL
   - Or use Let's Encrypt

**Example Custom Domain:**
`www.viswam-edutech.com` → Your hosting

---

## Recommended Setup for Production

### **Best Combination:**
1. **Frontend Hosting:** Netlify or Vercel (FREE)
2. **Custom Domain:** Namecheap ($5/year)
3. **Email:** Gmail (FREE)
4. **Database:** Firebase (FREE tier generous)
5. **SSL:** Auto-included

**Total Cost:** ~$5-10/year

---

## Quick Comparison Table

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| GitHub Pages | FREE | 10 min | Static sites |
| Netlify | FREE | 2 min | Easy deployment |
| Vercel | FREE | 5 min | Projects |
| Firebase | FREE | 15 min | With backend |
| Bluehost | $2.95/mo | 20 min | Professional |
| AWS | $1-20/mo | 30 min | Scalable |
| Google Cloud | $5-50/mo | 30 min | Enterprise |

---

## Troubleshooting

### **"404 Not Found"**
- Make sure file is named `index.html`
- Check if file was uploaded correctly

### **"Data not saving"**
- Browser might be clearing localStorage
- Enable in browser settings
- Or migrate to backend database

### **"Site not loading"**
- Check internet connection
- Clear browser cache
- Try different browser
- Wait 5 minutes for deployment

### **"Can't login"**
- Check demo credentials
- Admin: admin@school.edu / admin123
- Student: john@school.edu / student123
- Make sure you selected correct role

---

## Next Steps for Production

1. ✅ Deploy on Netlify/GitHub Pages (TODAY)
2. ✅ Get custom domain ($5/year)
3. ✅ Add backend database (optional)
4. ✅ Set up email notifications (optional)
5. ✅ Add payment integration (if needed)
6. ✅ Increase security & SSL

---

## Contact & Support

- **Demo Credentials:**
  - Admin: admin@school.edu / admin123
  - Student: john@school.edu / student123

- **Features:**
  - Admin: Create papers, manage students, bulk upload
  - Student: Take exams, view results, practice

- **All data saved locally** - No server needed for basic use

---

## Summary

**Fastest Way to Go Live:**

1. Save file as `index.html`
2. Go to netlify.com
3. Drag & drop file
4. **LIVE in 30 seconds!**

**Total Cost:** FREE

**That's it! 🚀**
