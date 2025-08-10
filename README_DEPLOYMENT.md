# Deployment Instructions with Password Protection

## Setting Up Password Protection

The app now includes password protection. The default password for local testing is: `pdfcombiner123`

### For Local Development
The password is stored in `.streamlit/secrets.toml` (this file is gitignored for security).

### For Streamlit Cloud Deployment

1. **Deploy the app** as usual on https://share.streamlit.io/

2. **Set up the password** in Streamlit Cloud:
   - Go to your app's dashboard on Streamlit Cloud
   - Click on the three dots menu (⋮) next to your app
   - Select "Settings"
   - Go to the "Secrets" section
   - Add the following:
   ```toml
   password = "your-secure-password-here"
   ```
   - Click "Save"

3. **Important Security Notes:**
   - Change the default password to something secure
   - Never commit the actual password to your repository
   - The `.streamlit/secrets.toml` file is gitignored for security
   - Share the password only with authorized users

## Features Added

1. **Login Screen**: Users must enter the password to access the app
2. **Session Management**: Password is validated securely using HMAC
3. **Logout Button**: Users can logout from the main interface
4. **Secure Storage**: Passwords are stored in Streamlit's secrets management

## Testing the Password Protection

1. Run the app locally:
   ```bash
   streamlit run app.py
   ```

2. You'll see a login screen asking for a password

3. Enter: `pdfcombiner123` (or your custom password)

4. After successful login, you can use the PDF combiner

5. Click "Logout" to end your session

## Customizing the Password

### For Local Development:
Edit `.streamlit/secrets.toml`:
```toml
password = "your-new-password"
```

### For Production (Streamlit Cloud):
Use the Streamlit Cloud secrets management as described above.

## Security Best Practices

1. Use a strong password (mix of letters, numbers, special characters)
2. Change the password regularly
3. Don't share the password in public channels
4. Consider using different passwords for development and production
5. Monitor access logs if available