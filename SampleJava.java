/**
 * Simple Java class for testing the Mermaid flowchart generator.
 */
public class SampleJava {
    
    private int counter = 0;

    /**
     * Simple method with basic control flow.
     */
    public void simpleMethod(int x) {
        if (x > 0) {
            System.out.println("Positive");
        } else {
            System.out.println("Non-positive");
        }
    }

    /**
     * Method with multiple return paths.
     */
    public String validateUser(String username, String password) {
        if (username == null || username.isEmpty()) {
            return "Invalid username";
        }
        
        if (password == null || password.length() < 8) {
            return "Password too short";
        }
        
        return "Valid user";
    }
}