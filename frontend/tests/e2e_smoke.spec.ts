import { test, expect } from '@playwright/test';

test.describe('MarketVerify Frontend E2E Smoke Test', () => {
  test('submits a market claim and displays live agent trace and final verdict', async ({ page }) => {
    // 1. Visit homepage
    await page.goto('/');

    // 2. Assert Header brand and status
    await expect(page.locator('text=MARKETVERIFY')).toBeVisible();
    await expect(page.locator('text=Verify Indian Market Rumor')).toBeVisible();

    // 3. Click one of the 1-Click Demo Scenario presets
    const presetButton = page.locator('button:has-text("Reliance Zepto 40% Stake Buyout")');
    await expect(presetButton).toBeVisible();
    await presetButton.click();

    // 4. Submit claim form
    const submitButton = page.locator('button:has-text("Execute Multi-Agent Verification")');
    await expect(submitButton).toBeVisible();
    await submitButton.click();

    // 5. Assert navigation to Agent Trace view
    await expect(page.locator('text=CLAIM TRACE:')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=LangGraph Multi-Agent Orchestration Topology')).toBeVisible();

    // 6. Assert all 5 agent nodes exist in DAG
    await expect(page.locator('text=Normalizer Agent')).toBeVisible();
    await expect(page.locator('text=Trust-Tier Agent')).toBeVisible();
    await expect(page.locator('text=Verification Agent')).toBeVisible();
    await expect(page.locator('text=Sentiment Agent')).toBeVisible();
    await expect(page.locator('text=Aggregator Verdict')).toBeVisible();

    // 7. Wait for completion and assert final verdict banner or citations list
    await expect(page.locator('text=CORROBORATED BY OFFICIAL FILING').or(page.locator('text=TRACE REPLAY COMPLETE'))).toBeVisible({
      timeout: 20000,
    });
  });
});
