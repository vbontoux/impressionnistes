#!/usr/bin/env node

/**
 * Generate PNG icons from the Impressionnistes logo
 * Run: node generate-icons.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const publicDir = path.join(__dirname, 'public');
const logoPath = path.join(publicDir, 'logo-source.jpg');

// Icon sizes to generate
const icons = [
  { name: 'favicon-16x16.png', size: 16 },
  { name: 'favicon-32x32.png', size: 32 },
  { name: 'apple-touch-icon.png', size: 180 },
  { name: 'icon-192.png', size: 192 },
  { name: 'icon-512.png', size: 512 },
];

async function generateIcons() {
  console.log('🎨 Generating icons from impressionnistes-logo.jpg...');
  console.log('');

  if (!fs.existsSync(logoPath)) {
    console.error('❌ logo-source.jpg not found in public directory');
    console.error('Please copy the logo: cp src/assets/impressionnistes-logo.jpg public/logo-source.jpg');
    process.exit(1);
  }

  // Get logo dimensions to determine if we need to crop or pad
  const metadata = await sharp(logoPath).metadata();
  console.log(`📐 Source logo: ${metadata.width}x${metadata.height}`);
  console.log('');

  for (const icon of icons) {
    const outputPath = path.join(publicDir, icon.name);
    
    try {
      // For square icons, we need to handle the rectangular logo
      // Option 1: Contain (add padding) - keeps full logo visible
      // Option 2: Cover (crop) - fills square but may cut off parts
      
      // Using 'contain' with white background to keep full logo visible
      await sharp(logoPath)
        .resize(icon.size, icon.size, {
          fit: 'contain',
          background: { r: 255, g: 255, b: 255, alpha: 1 }
        })
        .png()
        .toFile(outputPath);
      
      console.log(`  ✓ ${icon.name} (${icon.size}x${icon.size})`);
    } catch (error) {
      console.error(`  ✗ Failed to generate ${icon.name}:`, error.message);
    }
  }

  // Also create favicon.ico for maximum browser compatibility
  try {
    const faviconIcoPath = path.join(publicDir, 'favicon.ico');
    await sharp(path.join(publicDir, 'favicon-32x32.png'))
      .resize(32, 32)
      .png()
      .toFile(faviconIcoPath);
    console.log(`  ✓ favicon.ico (32x32)`);
  } catch (error) {
    console.error(`  ✗ Failed to generate favicon.ico:`, error.message);
  }

  console.log('');
  console.log('✅ All icons generated successfully from the Impressionnistes logo!');
  console.log('');
  console.log('⚠️  Important: Clear your browser cache to see the new icons!');
  console.log('');
  console.log('To clear cache:');
  console.log('  - Chrome/Edge: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)');
  console.log('  - Firefox: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)');
  console.log('  - Safari: Cmd+Option+E, then reload');
  console.log('');
  console.log('Next steps:');
  console.log('  1. Test the icons by running: npm run dev');
  console.log('  2. Check browser tab for favicon');
  console.log('  3. Test "Add to Home Screen" on iOS and Android');
  console.log('');
}

generateIcons().catch(error => {
  console.error('❌ Error generating icons:', error);
  process.exit(1);
});
