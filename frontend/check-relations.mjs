import { chromium } from '@playwright/test'

async function checkRelationsTab() {
  const browser = await chromium.launch({ headless: false })
  const page = await browser.newPage()

  try {
    console.log('🌐 Navigating to http://localhost:5174...')
    await page.goto('http://localhost:5174')
    await page.waitForLoadState('networkidle')

    console.log('📸 Taking homepage screenshot...')
    await page.screenshot({ path: 'screenshots/01-homepage.png', fullPage: true })

    console.log('🖱️  Clicking Relations tab...')
    await page.click('text=Relations')
    await page.waitForTimeout(1000)

    console.log('📸 Taking Relations tab screenshot...')
    await page.screenshot({ path: 'screenshots/02-relations-tab.png', fullPage: true })

    // Check what's rendered
    const debugPanel = await page.locator('text=Debug:').count()
    console.log('✅ Debug panel found:', debugPanel > 0)

    const loadButton = await page.locator('button:has-text("Load Token Graph")').count()
    console.log('✅ Load button found:', loadButton > 0)

    const graphDemo = await page.locator('text=Token Graph Demo').count()
    console.log('✅ Token Graph Demo found:', graphDemo > 0)

    // Get debug info
    if (debugPanel > 0) {
      const debugText = await page.locator('div:has-text("Debug:")').first().textContent()
      console.log('📊 Debug info:', debugText)
    }

    // Click load button if it exists
    if (loadButton > 0) {
      console.log('🔘 Clicking load button...')

      // Listen for console messages
      page.on('console', msg => console.log('Browser console:', msg.text()))

      await page.click('button:has-text("Load Token Graph")')
      await page.waitForTimeout(3000)

      console.log('📸 Taking after-load screenshot...')
      await page.screenshot({ path: 'screenshots/03-after-load.png', fullPage: true })

      // Check if tokens appeared
      const allTokensText = await page.locator('text=All Tokens').count()
      console.log('✅ "All Tokens" header found:', allTokensText > 0)
    }

    // Get full Relations content
    const content = await page.locator('section.panel').filter({ hasText: 'Relations' }).textContent()
    console.log('\n📄 Relations Tab Content (first 500 chars):')
    console.log(content?.substring(0, 500))

    console.log('\n✅ Test complete! Check screenshots/ directory')
    console.log('Press Ctrl+C to close browser')

    // Keep browser open for manual inspection
    await page.waitForTimeout(300000) // 5 minutes

  } catch (error) {
    console.error('❌ Error:', error)
  } finally {
    await browser.close()
  }
}

checkRelationsTab()
