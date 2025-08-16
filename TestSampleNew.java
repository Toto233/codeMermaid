/**
 * Sample Java class for testing the Mermaid flowchart generator.
 * This is a clean version without existing Mermaid comments.
 */
public class TestSampleNew {
    
    private int counter;
    private String name;
    
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
    /**
     * Method flowchart visualization.
     *
     * @mermaid
     * ```mermaid
     * flowchart TD
     * Start((Start))
     * End((End))
     * Start --> ValidateInput{input == null\nor input.isEmpty()?}
     * ValidateInput -->|Yes| ThrowException[[throw IllegalArgumentException]]
     * ValidateInput -->|No| SwitchValue{switch (value)}
     * SwitchValue -->|1| ProcessSingle[[result = processSingleValue(input)]]
     * SwitchValue -->|2| ProcessDouble[[result = processDoubleValue(input)]]
     * SwitchValue -->|default| ProcessMultiple[[result = processMultipleValues(value, input)]]
     * ProcessSingle --> InitLoop
     * ProcessDouble --> InitLoop
     * ProcessMultiple --> InitLoop
     * InitLoop[/i = 0/] --> LoopCheck{i < value?}
     * LoopCheck -->|Yes| Concat[[result += "_" + i]]
     * Concat --> EvenCheck{i % 2 == 0?}
     * EvenCheck -->|Yes| Upper[[result = result.toUpperCase()]]
     * EvenCheck -->|No| Lower[[result = result.toLowerCase()]]
     * Upper --> Increment[/i++/]
     * Lower --> Increment
     * Increment --> LoopCheck
     * LoopCheck -->|No| TryBlock
     * TryBlock[[result = riskyOperation(result)]] --> FinallyBlock
     * TryBlock -.->|RuntimeException| CatchBlock[[result = "error"]]
     * CatchBlock --> FinallyBlock
     * FinallyBlock[/counter++/] --> ReturnResult[/return result/]
     * ReturnResult --> End
     * ThrowException --> End
     * ```
     *
     * To extract clean Mermaid code:
     * 1. Copy lines between the ```mermaid and ``` markers
     * 2. Remove the leading asterisks and spaces
     * OR
     * 1. Use the generated .mmd file in the output directory
     */
    public String complexMethod(int value, String input) throws Exception {
        String result = "";
        
        // Input validation
        if (input == null || input.isEmpty()) {
            throw new IllegalArgumentException("Input cannot be null or empty");
        }
        
        // Process based on value
        switch (value) {
            case 1:
                result = processSingleValue(input);
                break;
            case 2:
                result = processDoubleValue(input);
                break;
            default:
                result = processMultipleValues(value, input);
        }
        
        // Additional processing
        for (int i = 0; i < value; i++) {
            result += "_" + i;
            
            if (i % 2 == 0) {
                result = result.toUpperCase();
            } else {
                result = result.toLowerCase();
            }
        }
        
        // Exception handling
        try {
            result = riskyOperation(result);
        } catch (RuntimeException e) {
            result = "error";
        } finally {
            counter++;
        }
        
        return result;
    }
    
    private String processSingleValue(String input) {
        return "single:" + input;
    }
    
    private String processDoubleValue(String input) {
        return "double:" + input + input;
    }
    
    private String processMultipleValues(int count, String input) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append(input).append(i);
        }
        return sb.toString();
    }
    
    private String riskyOperation(String input) throws RuntimeException {
        if (input.contains("error")) {
            throw new RuntimeException("Simulated error");
        }
        return input.toUpperCase();
    }
    
    /**
     * Method with nested loops and conditions.
     */
    public int calculateFactorial(int n) {
        if (n < 0) {
            return -1;
        }
        
        int result = 1;
        for (int i = 1; i <= n; i++) {
            result *= i;
        }
        
        return result;
    }
    /**
    /**
     * Method flowchart visualization.
     *
     * @mermaid
     * ```mermaid
     * flowchart TD
     * A((Start)) --> B{username == null\nor\nusername.isEmpty()}
     * B -->|true| C[/"return \"Invalid username\""\]
     * B -->|false| D{password == null\nor\npassword.length() < 8}
     * D -->|true| E[/"return \"Password too short\""\]
     * D -->|false| F{!password.matches\n(".*[A-Z].*")}
     * F -->|true| G[/"return \"Missing uppercase letter\""\]
     * F -->|false| H[/"return \"Valid user\""\]
     * C --> I((End))
     * E --> I
     * G --> I
     * H --> I
     * ```
     *
     * To extract clean Mermaid code:
     * 1. Copy lines between the ```mermaid and ``` markers
     * 2. Remove the leading asterisks and spaces
     * OR
     * 1. Use the generated .mmd file in the output directory
     */
    public String validateUser(String username, String password) {
        if (username == null || username.isEmpty()) {
            return "Invalid username";
        }
        
        if (password == null || password.length() < 8) {
            return "Password too short";
        }
        
        if (!password.matches(".*[A-Z].*")) {
            return "Missing uppercase letter";
        }
        
        return "Valid user";
    }
}