# Railway Monorepo Configuration Fix

## Problem

Railway is using the OLD Dockerfiles in subdirectories instead of the new root-level Dockerfiles.

## Solution: Update Railway Service Settings

For **fraud-api**, **ecommerce-api**, and **hr-api**, you need to manually configure Railway:

### Step-by-Step Instructions:

1. **Go to Railway Dashboard** → Your Project

2. **For EACH failing service** (fraud-api, ecommerce-api, hr-api):

   a. Click on the service name

   b. Go to **Settings** tab

   c. Scroll to **Build** section

   d. Find **"Root Directory"**:

   - Set to: **`.`** or **`/`** (the repository root)
   - If it shows `fraud/` or `ecommerce/` or `hr/` - DELETE that

   e. Find **"Dockerfile Path"**:

   - fraud-api: Set to `Dockerfile.fraud`
   - ecommerce-api: Set to `Dockerfile.ecommerce`
   - hr-api: Set to `Dockerfile.hr`

   f. **Save** and **Redeploy** the service

### Visual Guide:

```
Service Settings → Build Configuration
┌─────────────────────────────────────┐
│ Root Directory: .                   │  ← Must be root, not fraud/
├─────────────────────────────────────┤
│ Dockerfile Path: Dockerfile.fraud   │  ← Points to root-level file
└─────────────────────────────────────┘
```

### Alternative: Delete and Recreate Services

If Railway doesn't let you change Root Directory:

1. **Delete** the failing service (fraud-api, ecommerce-api, hr-api)
2. **Create New Service** → "Deploy from GitHub repo"
3. When prompted:
   - Root Directory: `.` (root)
   - Dockerfile Path: `Dockerfile.fraud` (or .ecommerce or .hr)
4. Add environment variables (copy from old service if needed)
5. Deploy

## Why This Happened

Railway created services pointing to subdirectory Dockerfiles (`fraud/Dockerfile`) BEFORE we created the root-level ones (`Dockerfile.fraud`). The `railway.toml` files don't override existing service configurations.

## What We Fixed

- ✅ Created `Dockerfile.{service}` at repository root
- ✅ These Dockerfiles can access `shared/` folder
- ✅ Created `railway.toml` files (for NEW services)
- ⚠️ Need to update EXISTING services manually in dashboard

## After Fix

All 6 APIs should deploy successfully:

- fraud-api → uses `Dockerfile.fraud` from root
- ecommerce-api → uses `Dockerfile.ecommerce` from root
- financial-api → uses `Dockerfile.financial` from root (already working)
- healthcare-api → uses `Dockerfile.healthcare` from root (already working)
- hr-api → uses `Dockerfile.hr` from root
- restaurant-api → uses `Dockerfile.restaurant` from root (already working)
