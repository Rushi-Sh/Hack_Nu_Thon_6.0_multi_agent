const {Builder, By, Key, until} = require('selenium-webdriver');
const assert = require('assert');

describe('Website UI Tests', () => {
    let driver;

    before(async () => {
        driver = await new Builder().forBrowser('chrome').build();
    });

    after(async () => {
        await driver.quit();
    });


    it('Verify login button is clickable', async () => {
        await driver.get('file:///path/to/your/index.html'); // Replace with your index.html file path

        // Assuming login link is './HTML files/authentication.html'
        const loginLink = await driver.findElement(By.css("a[href*='authentication.html']")); 
        assert(await loginLink.isDisplayed(), "Login link is not displayed");
        await loginLink.click();
        // Add a wait for the authentication page to load (adjust as needed)
        await driver.wait(until.urlContains('authentication.html'), 5000);


    });


    it('Fill the login form with valid credentials and submit', async () => {
      // Assuming you are already on the login page from the previous test
      
      // Replace with your actual login form element locators
      const usernameField = await driver.findElement(By.id('username')); // Replace 'username' with the actual ID
      const passwordField = await driver.findElement(By.id('password')); // Replace 'password' with the actual ID
      const submitButton = await driver.findElement(By.id('loginButton'));  // Replace 'loginButton' with the actual ID/selector



      await usernameField.sendKeys('testuser');  // Replace with valid username
      await passwordField.sendKeys('testpassword'); // Replace with valid password
      await submitButton.click();

      // Add assertions to verify successful login.  Example: Check for a welcome message, URL change, etc.
      // Example URL check:
      // await driver.wait(until.urlContains('dashboard'), 5000); 
      

    });



    it('Ensure the logout button is visible after login', async () => {
        // Assuming you are logged in from the previous test
        // Replace with your actual logout button locator
        const logoutButton = await driver.findElement(By.id('logoutButton'));  // Replace 'logoutButton' with actual ID/selector
        assert(await logoutButton.isDisplayed(), "Logout button is not displayed");


    });


});