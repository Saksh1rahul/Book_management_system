import { test as baseTest } from '@playwright/test';

const TEST_USER = { username: 'playwright', password: 'playwright123' };

async function ensureAuthenticated(page) {
  const backendUrl = 'http://127.0.0.1:5000';

  try {
    await fetch(`${backendUrl}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(TEST_USER),
    });
  } catch (error) {
    // Ignore registration errors and continue to login
  }

  const loginResponse = await fetch(`${backendUrl}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(TEST_USER),
  });

  if (!loginResponse.ok) {
    throw new Error(`Login failed with status ${loginResponse.status}`);
  }

  const { token, username } = await loginResponse.json();
  await page.evaluate(({ authToken, authUsername }) => {
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', authUsername);
  }, { authToken: token, authUsername: username });
}

export const test = baseTest.extend({
  page: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    const page = await context.newPage();

    await page.goto('http://localhost:5173');
    await ensureAuthenticated(page);
    await page.reload();

    await use(page);

    await context.close();
  },
});

export const expect = test.expect;