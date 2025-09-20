import { 
  CognitoIdentityProviderClient, 
  InitiateAuthCommand, 
  RespondToAuthChallengeCommand,
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
 * Authenticates a user with Cognito, handling the NEW_PASSWORD_REQUIRED challenge.
 * @param {string} username - The user's username.
 * @param {string} password - The user's temporary or permanent password.
 * @returns {Promise<object>} The AuthenticationResult object from Cognito, containing tokens.
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

    // Case 2: First-time login with temporary password, new password required
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

    // Case 3: Unexpected response from Cognito
    throw new Error("Authentication failed. Unexpected response from Cognito.");

  } catch (error) {
    console.error("Cognito sign-in error object:", error); // Log the full error object
    // Re-throw a more user-friendly error message
    throw new Error(error.message || "An error occurred during sign-in.");
  }
}
