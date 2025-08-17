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
     * Method flowchart visualization.
     *
     * @mermaid
     * ```mermaid
     * flowchart TD
     * Start((开始))
     * ValidateInput{输入是否为空}
     * ThrowEx[抛出IllegalArgumentException]
     * SwitchValue{value值}
     * ProcSingle[调用processSingleValue]
     * ProcDouble[调用processDoubleValue]
     * ProcMulti[调用processMultipleValues]
     * InitLoop[/i初始化为0/]
     * CheckLoop{i < value}
     * AppendIndex[追加"_"+i]
     * CheckEven{i为偶数}
     * ToUpper[转大写]
     * ToLower[转小写]
     * IncrI[/i自增/]
     * TryRisky{调用riskyOperation}
     * CatchEx[捕获RuntimeException并置result为"error"]
     * IncrCounter[counter自增]
     * End((返回result))
     * Start --> ValidateInput
     * ValidateInput -->|是| ThrowEx
     * ValidateInput -->|否| SwitchValue
     * ThrowEx -.-> End
     * SwitchValue -->|1| ProcSingle
     * SwitchValue -->|2| ProcDouble
     * SwitchValue -->|其他| ProcMulti
     * ProcSingle --> InitLoop
     * ProcDouble --> InitLoop
     * ProcMulti --> InitLoop
     * InitLoop --> CheckLoop
     * CheckLoop -->|是| AppendIndex
     * AppendIndex --> CheckEven
     * CheckEven -->|是| ToUpper
     * CheckEven -->|否| ToLower
     * ToUpper --> IncrI
     * ToLower --> IncrI
     * IncrI --> CheckLoop
     * CheckLoop -->|否| TryRisky
     * TryRisky -->|正常| IncrCounter
     * TryRisky -.->|RuntimeException| CatchEx
     * CatchEx --> IncrCounter
     * IncrCounter --> End
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
     * Method flowchart visualization.
     *
     * @mermaid
     * ```mermaid
     * flowchart TD
     * A((Start)) --> B{username == null or username.isEmpty()}
     * B -->|true| C[/return "Invalid username"/]
     * B -->|false| D{password == null or password.length() < 8}
     * D -->|true| E[/return "Password too short"/]
     * D -->|false| F{!password.matches("\\\\.*[A-Z].*")}
     * F -->|true| G[/return "Missing uppercase letter"/]
     * F -->|false| H[/return "Valid user"/]
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