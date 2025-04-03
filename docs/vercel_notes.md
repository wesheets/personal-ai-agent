# Vercel Deployment Notes

## Path Context in Vercel Deployments

### Important Notes:
- Prefixing paths in build commands should only be used if Vercel's root is at the monorepo root.
- Always verify the working directory context before assuming paths.
- Vercel operates inside the app/frontend directory by default when the Root Directory is set to app/frontend.
- Using prefixes like `--prefix app/frontend` when already in that directory causes double path errors.

### Lessons Learned:
1. Never assume the working directory without verification
2. Always add logging commands (pwd, ls) to verify the actual working context
3. Test with minimal changes first to understand the environment
4. Follow the "Manus Clause": If you can't prove it, don't say it

### Current Configuration:
```json
{
  "buildCommand": "pwd && ls -la && npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### Vercel Dashboard Settings:
- Root Directory: app/frontend
- Framework Preset: Vite
