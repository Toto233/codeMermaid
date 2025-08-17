import java.util.Scanner;

public class FibonacciIterative {
    /**
     * Method flowchart visualization.
     *
     * @mermaid
     * ```mermaid
     * flowchart TD
     * Start((开始))
     * CheckBase{n≤1}
     * ReturnN[直接返回n]
     * InitVars[/初始化a=0, b=1/]
     * LoopHead{i从2到n}
     * CalcCurrent[current = a + b]
     * ShiftA[a = b]
     * ShiftB[b = current]
     * LoopEnd[/i++/]
     * ReturnB[返回b]
     * End((结束))
     * Start --> CheckBase
     * CheckBase -->|是| ReturnN
     * CheckBase -->|否| InitVars
     * InitVars --> LoopHead
     * LoopHead -->|i≤n| CalcCurrent
     * CalcCurrent --> ShiftA
     * ShiftA --> ShiftB
     * ShiftB --> LoopEnd
     * LoopEnd --> LoopHead
     * LoopHead -->|i>n| ReturnB
     * ReturnN --> End
     * ReturnB --> End
     * ```
     *
     * To extract clean Mermaid code:
     * 1. Copy lines between the ```mermaid and ``` markers
     * 2. Remove the leading asterisks and spaces
     * OR
     * 1. Use the generated .mmd file in the output directory
     */

    /**
     * 使用迭代法计算斐波那契数列的第 n 项
     * @param n 要计算的项数 (n >= 0)
     * @return 斐波那契数列的第 n 项的值
     */
    public static long fibonacci(int n) {
        // 处理基础情况：F(0) = 0, F(1) = 1
        if (n <= 1) {
            return n;
        }

        long a = 0; // 代表 F(n-2)
        long b = 1; // 代表 F(n-1)
        long current = 0; // 代表 F(n)

        // 从 2 开始循环直到 n
        for (int i = 2; i <= n; i++) {
            current = a + b; // F(i) = F(i-2) + F(i-1)
            a = b;           // 更新 a 为上一轮的 b
            b = current;     // 更新 b 为当前计算出的值
        }

        return b; // 循环结束后，b 的值就是 F(n)
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("请输入要计算的斐波那契数列的项数 n: ");
        int n = scanner.nextInt();

        if (n < 0) {
            System.out.println("输入无效，n 必须是大于等于0的整数。");
        } else {
            System.out.println("正在计算 F(" + n + ")...");
            long result = fibonacci(n);
            System.out.println("斐波那契数列的第 " + n + " 项是: " + result);
        }
        
        // 打印前 n+1 项
        System.out.println("\n斐波那契数列的前 " + (n + 1) + " 项为:");
        for (int i = 0; i <= n; i++) {
            System.out.print(fibonacci(i) + " ");
        }
        System.out.println();
        scanner.close();
    }
}