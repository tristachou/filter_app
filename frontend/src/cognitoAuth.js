import { 
  CognitoIdentityProviderClient, 
  InitiateAuthCommand, 
  RespondToAuthChallengeCommand,
  SignUpCommand,
  ConfirmSignUpCommand,
  AssociateSoftwareTokenCommand,
  VerifySoftwareTokenCommand,
  SetUserMFAPreferenceCommand, // Add this command
  GetUserCommand,
  AuthFlowType 
} from "@aws-sdk/client-cognito-identity-provider";
import HmacSHA256 from 'crypto-js/hmac-sha256';
import Base64 from 'crypto-js/enc-base64';

// --- Cognito Configuration --- //
const REGION = "ap-southeast-2";
const USER_POOL_ID = "ap-southeast-2_kddUAod7A";
const CLIENT_ID = "4h9hjhn6bfujbskpocnd9mticd";
const CLIENT_SECRET = "akudcqipabe14cd7kdb65hk751b9q33cs6c97r2a0llui1pj126";

// --- Cognito Client --- //
const client = new CognitoIdentityProviderClient({ region: REGION });

/**
 * Calculates the secret hash required by Cognito for app clients with a secret.
 * @param {string} username - The user's username.
 * @returns {string} The base64 encoded secret hash.
 */
function getSecretHash(username) {
  const hash = HmacSHA256(username + CLIENT_ID, CLIENT_SECRET);
  return Base64.stringify(hash);
}

/**
 * Authenticates a user with Cognito, handling MFA and NEW_PASSWORD_REQUIRED challenges.
 * @param {string} username - The user's username.
 * @param {string} password - The user's temporary or permanent password.
 * @returns {Promise<object>} The AuthenticationResult object from Cognito, or a challenge object.
 */
export async function signIn(username, password) {
  const initialAuthCommand = new InitiateAuthCommand({
    AuthFlow: AuthFlowType.USER_PASSWORD_AUTH,
    ClientId: CLIENT_ID,
    AuthParameters: {
      USERNAME: username,
      PASSWORD: password,
      SECRET_HASH: getSecretHash(username),
    },
  });

  try {
    const initialResponse = await client.send(initialAuthCommand);
    console.log("Cognito Raw Response:", initialResponse);

    // Case 1: Successful login with permanent password
    if (initialResponse.AuthenticationResult) {
      return initialResponse.AuthenticationResult;
    }

    // Case 2: MFA challenge required
    if (initialResponse.ChallengeName === 'SOFTWARE_TOKEN_MFA') {
      console.log("Handling SOFTWARE_TOKEN_MFA challenge.");
      return {
        challengeName: 'SOFTWARE_TOKEN_MFA',
        session: initialResponse.Session,
      };
    }

    // Case 3: First-time login with temporary password, new password required
    if (initialResponse.ChallengeName === 'NEW_PASSWORD_REQUIRED') {
      console.log("Handling NEW_PASSWORD_REQUIRED challenge.");
      const newPassword = "MyNewPassword123!"; // Hardcoded new password

      const respondToChallengeCommand = new RespondToAuthChallengeCommand({
        ChallengeName: 'NEW_PASSWORD_REQUIRED',
        ClientId: CLIENT_ID,
        ChallengeResponses: {
          USERNAME: username,
          NEW_PASSWORD: newPassword,
          SECRET_HASH: getSecretHash(username),
          'userAttributes.email': 'testuser@example.com', // Add required email attribute
        },
        Session: initialResponse.Session,
      });

      const challengeResponse = await client.send(respondToChallengeCommand);
      
      // After setting the new password, the tokens are in this response
      if (challengeResponse.AuthenticationResult) {
        console.log("Successfully set new password and received tokens.");
        return challengeResponse.AuthenticationResult;
      } else {
        // This would be an unexpected state
        throw new Error("Failed to set new password, no tokens returned.");
      }
    }

    // Case 4: Unexpected response from Cognito
    throw new Error("Authentication failed. Unexpected response from Cognito.");

  } catch (error) {
    console.error("Cognito sign-in error object:", error); // Log the full error object
    // Re-throw a more user-friendly error message
    throw new Error(error.message || "An error occurred during sign-in.");
  }
}

/**
 * Responds to the MFA challenge after initial sign-in.
 * @param {string} username - The user's username.
 * @param {string} mfaCode - The 6-digit code from the authenticator app.
 * @param {string} session - The session string from the initial sign-in response.
 * @returns {Promise<object>} The AuthenticationResult object from Cognito.
 */
export async function respondToMfaChallenge(username, mfaCode, session) {
  const command = new RespondToAuthChallengeCommand({
    ChallengeName: 'SOFTWARE_TOKEN_MFA',
    ClientId: CLIENT_ID,
    ChallengeResponses: {
      USERNAME: username,
      SOFTWARE_TOKEN_MFA_CODE: mfaCode,
      SECRET_HASH: getSecretHash(username),
    },
    Session: session,
  });

  try {
    const response = await client.send(command);
    if (response.AuthenticationResult) {
      console.log("Successfully verified MFA and received tokens.");
      return response.AuthenticationResult;
    }
    // This case should ideally not be reached if the code is correct
    throw new Error("MFA verification failed, no tokens returned.");
  } catch (error) {
    console.error("Cognito MFA challenge error:", error);
    throw new Error(error.message || "An error occurred during MFA verification.");
  }
}

/**
 * Registers a new user in the Cognito User Pool.
 * @param {string} username - The desired username.
 * @param {string} password - The desired password.
 * @param {string} email - The user's email address.
 * @returns {Promise<object>} The response from Cognito.
 */
export async function signUp(username, password, email) {
  const command = new SignUpCommand({
    ClientId: CLIENT_ID,
    Username: username,
    Password: password,
    SecretHash: getSecretHash(username),
    UserAttributes: [{ Name: "email", Value: email }],
  });

  try {
    const response = await client.send(command);
    return response;
  } catch (error) {
    console.error("Cognito sign-up error:", error);
    throw new Error(error.message || "An error occurred during sign-up.");
  }
}

/**
 * Confirms a user's registration with a confirmation code.
 * @param {string} username - The username of the user to confirm.
 * @param {string} confirmationCode - The code sent to the user's email.
 * @returns {Promise<object>} The response from Cognito.
 */
export async function confirmSignUp(username, confirmationCode) {
  const command = new ConfirmSignUpCommand({
    ClientId: CLIENT_ID,
    Username: username,
    ConfirmationCode: confirmationCode,
    SecretHash: getSecretHash(username),
  });

  try {
    const response = await client.send(command);
    return response;
  } catch (error) {
    console.error("Cognito confirmation error:", error);
    throw new Error(error.message || "An error occurred during confirmation.");
  }
}

/**
 * Begins the process of associating a software token for MFA.
 * @param {string} accessToken - The user's access token.
 * @returns {Promise<object>} The response from Cognito, containing the SecretCode.
 */
export async function associateSoftwareToken(accessToken) {
  const command = new AssociateSoftwareTokenCommand({
    AccessToken: accessToken,
  });

  try {
    const response = await client.send(command);
    return response;
  } catch (error) {
    console.error("Cognito associate software token error:", error);
    throw new Error(error.message || "Failed to start MFA setup.");
  }
}

/**
 * Verifies the software token and enables MFA.
 * @param {string} accessToken - The user's access token.
 * @param {string} userCode - The code from the authenticator app.
 * @returns {Promise<object>} The response from Cognito.
 */
export async function verifySoftwareToken(accessToken, userCode) {
  const command = new VerifySoftwareTokenCommand({
    AccessToken: accessToken,
    UserCode: userCode,
  });

  try {
    const response = await client.send(command);
    return response;
  } catch (error) {
    console.error("Cognito verify software token error:", error);
    throw new Error(error.message || "Failed to verify MFA code.");
  }
}

/**
 * Updates the user's MFA preference (enables or disables TOTP).
 * @param {string} accessToken - The user's access token.
 * @param {object} settings - The settings to apply, e.g., { Enabled: true, PreferredMfa: true }.
 * @returns {Promise<object>} The response from Cognito.
 */
export async function updateMfaPreference(accessToken, settings) {
  const command = new SetUserMFAPreferenceCommand({
    AccessToken: accessToken,
    SoftwareTokenMfaSettings: settings,
  });

  try {
    const response = await client.send(command);
    console.log("Successfully updated MFA preference.", response);
    return response;
  } catch (error) {
    console.error("Cognito update MFA preference error:", error);
    throw new Error(error.message || "Failed to update MFA preference.");
  }
}

/**
 * Fetches the current user's details using their access token.
 * @param {string} accessToken - The user's access token.
 * @returns {Promise<object>} The user object from Cognito.
 */
export async function getUser(accessToken) {
  const command = new GetUserCommand({ AccessToken: accessToken });
  try {
    const response = await client.send(command);
    return response;
  } catch (error) {
    console.error("Cognito get user error:", error);
    throw new Error(error.message || "Failed to fetch user details.");
  }
}
