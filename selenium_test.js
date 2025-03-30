const { Builder, By, Key, until } = require('selenium-webdriver');
const { describe, it, before, after } = require('mocha');
const assert = require('assert');

describe('Login Functionality Tests', function() {
  let driver;
  const baseUrl = 'YOUR_WEBSITE_URL'; // Replace with your website URL
  const username = 'YOUR_USERNAME'; // Replace with your username
  const password = 'YOUR_PASSWORD'; // Replace with your password

  before(async function() {
    driver = await new Builder().forBrowser('chrome').build();
  });

  after(async function() {
    await driver.quit();
  });

  it('Verify login button is clickable', async function() {
    await driver.get(baseUrl);
    // Assuming the login button has an ID or class, replace 'loginButtonId' with the correct locator
    try {
      const loginButton = await driver.findElement(By.id('loginButtonId')); // Example locator
      await loginButton.click();
      // If the click doesn't throw an error, it's considered clickable
      assert.ok(true, 'Login button is clickable');
    } catch (error) {
      assert.fail('Login button is not clickable or not found: ' + error.message);
    }
  });

  it('Fill the login form with valid credentials and submit', async function() {
    await driver.get(baseUrl);
    // Assuming you have username and password input fields and a submit button
    try {
      const usernameField = await driver.findElement(By.id('username')); // Replace with actual ID
      const passwordField = await driver.findElement(By.id('password')); // Replace with actual ID
      const submitButton = await driver.findElement(By.id('submitButton')); // Replace with actual ID

      await usernameField.sendKeys(username);
      await passwordField.sendKeys(password);
      await submitButton.click();

      // Wait for some indication of successful login (e.g., page change, element visibility)
      await driver.wait(until.urlContains('dashboard'), 10000); // Adjust timeout as needed

      assert.ok(true, 'Login successful');
    } catch (error) {
      assert.fail('Login failed: ' + error.message);
    }
  });

  it('Ensure the logout button is visible after login', async function() {
    await driver.get(baseUrl);

    // Login first
    try {
        const usernameField = await driver.findElement(By.id('username')); // Replace with actual ID
        const passwordField = await driver.findElement(By.id('password')); // Replace with actual ID
        const submitButton = await driver.findElement(By.id('submitButton')); // Replace with actual ID

        await usernameField.sendKeys(username);
        await passwordField.sendKeys(password);
        await submitButton.click();

        await driver.wait(until.urlContains('dashboard'), 10000); // Adjust timeout as needed
    } catch (loginError) {
        assert.fail('Login failed before checking logout button: ' + loginError.message);
    }


    // Check for logout button visibility
    try {
      const logoutButton = await driver.findElement(By.id('logoutButton')); // Replace with actual ID
      const isDisplayed = await logoutButton.isDisplayed();
      assert.ok(isDisplayed, 'Logout button is visible after login');
    } catch (error) {
      assert.fail('Logout button is not visible after login: ' + error.message);
    }
  });
});