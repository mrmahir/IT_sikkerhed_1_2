# IT-Sikkerhed Projekt

Dette er et **skoleprojekt** for Zealand, Næstved (IT-Sikkerhed).

## Om Projektet
Under construction...

## Nyttige Links
* [Zealand - Sjællands Erhvervsakademi](https://www.zealand.dk/)
* [Markdown Guide](https://www.markdownguide.org/cheat-sheet/)

## 1.0 pytest
![alt text](image.png)

## 1.1 my own pytest
![alt text](image-1.png)

## 2.0 Test Strategies Assignment
**Topic:** Secure User Authentication & Password Policy

### 2.1 Equivalence Classes (Ækvivalensklasser)
We divide input data for password validation into classes that should be treated similarly.
* **Class 1 (Valid):** String length 8-64 characters, contains 1 special char, 1 digit.
* **Class 2 (Invalid):** String length < 8 characters.
* **Class 3 (Invalid):** String length > 64 characters.
* **Class 4 (Invalid):** Missing special character or digit.

### 2.2 Boundary Value Test (Grænseværditest)
We test the edges of the equivalence classes (specifically length requirements).
* **Test 7 chars:** Fail (Just below boundary)
* **Test 8 chars:** Pass (On boundary)
* **Test 64 chars:** Pass (On boundary)
* **Test 65 chars:** Fail (Just above boundary)

### 2.3 CRUD(L)
Mapping the Create, Read, Update, Delete, List operations to the Security Context:
* **C:** Register new user (hashing password).
* **R:** Login / Validate credentials (verify hash).
* **U:** Change password / Update profile 2FA settings.
* **D:** Delete account (GDPR compliance).
* **L:** List active sessions (for detecting suspicious activity).

### 2.4 Cycle Process Test
Testing the lifecycle of a user's security status:
1.  **State:** Account Active.
2.  **Action:** 3 Failed Login Attempts -> **State:** Account Locked.
3.  **Action:** Admin Unlock / Time expires -> **State:** Account Active.
4.  **Action:** Password Expired -> **State:** Awaiting Change.

### 2.5 Test Pyramid (Test Pyramiden)
Where these tests belong in the hierarchy:
* **Unit Tests (Base):** Decision table for login logic, Password complexity regex checks. (Fast, isolated).
* **Integration Tests (Middle):** Testing the "Create User" flow ensuring the database correctly stores the salted hash.
* **UI/E2E Tests (Top):** Selenium/Playwright script actually opening the browser and logging in.

### 2.6 Decision Table Test
Logic for `login(username, password)`:

| Rule | User Exists? | Account Locked? | Password Correct? | Expected Result |
| :--- | :----------- | :-------------- | :---------------- | :-------------- |
| 1    | False        | -               | -                 | Error: Invalid User |
| 2    | True         | True            | -                 | Error: Locked |
| 3    | True         | False           | False             | Error: Invalid Password |
| 4    | True         | False           | True              | Success |

### 2.7 Security Gates
Where in the CI/CD pipeline would I place these tests?
* **Commit Gate / Pull Request:** Run **Unit Tests** (Equivalence, Boundary, Decision Table). These must pass before code is merged.
* **Acceptance Test Gate:** Run **CRUD(L) Integration Tests** against a staging database.
* **Deployment Gate:** Run **Cycle Process** and E2E tests to ensure critical flows work in the final environment.

### 2.8 Screenshots

![alt text](image-3.png)

![alt text](image-2.png)