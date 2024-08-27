# coding=utf-8
from flask import Flask, request, jsonify
from zhipuai import ZhipuAI
import json

app = Flask(__name__)

model = "glm-4-air"
client = ZhipuAI(api_key="df5d42299e32adada7b7979ffd2e0aa9.vOe3VqH8aKxWVWy2")

prompt = """
请你根据要求, 参照样例来完成SCL编程任务
输出时请不要包含除代码外任何东西, 代码中也无需包含注释
每道题目为一段JSON格式的文字，即对题目的格式化描述，选手需要对照各字段构建输入格式。
各字段的含义如下：
- `title`：题目标题
- `description`：题目的文字描述
- `type`：需要生成的块类型，分为`FUNCTION`与`FUNCTION_BLOCK`，详见 SCL 相关资料
- `name`：块的名称
- `input`：块接口的 input 参数
  - `name`：参数名称
  - `type`：参数类型
  - `description`：参数的文字描述
  - `fields`：只会在参数类型为结构体`Struct`时出现，结构体的成员
    - `name`：结构体成员名称
    - `type`：结构体成员类型
    - `description`：结构体成员的文字描述
- `output`：块接口的 output 参数
  - `name`：参数名称
  - `type`：参数类型
  - `description`：参数的文字描述
  - `fields`：只会在参数类型为结构体`Struct`时出现，结构体的成员
    - `name`：结构体成员名称
    - `type`：结构体成员类型
    - `description`：结构体成员的文字描述
- `in/out`：块接口的 in/out 参数
  - `name`：参数名称
  - `type`：参数类型
  - `description`：参数的文字描述
  - `fields`：只会在参数类型为结构体`Struct`时出现，结构体的成员
    - `name`：结构体成员名称
    - `type`：结构体成员类型
    - `description`：结构体成员的文字描述
- `return_value`：只会在块类型为`FUNCTION`时出现，函数的返回值
  - `type`：返回值类型
  - `description`：返回值的文字描述
  - `fields`：只会在返回值类型为结构体`Struct`时出现，结构体的成员
    - `name`：结构体成员名称
    - `type`：结构体成员类型
    - `description`：结构体成员的文字描述
例子
题目一输入:
{
    "title": "双字边沿检测",
    "description": "编写一个函数块FB，该函数块每周期检查一个双字（DWord）输入值中的每一位的上升沿和下降沿。函数块应能够检测并报告输入值中的变化、上升边沿和下降边沿。
示例：
假设输入值从2#101变为2#11011，则上升沿数量为3，上升边沿的位流为2#11010，下降沿数量为1，下降边沿的位流为2#100。",
    "type": "FUNCTION_BLOCK",
    "name": "GetBitStates",
    "input": [
        {
            "name": "value",
            "type": "DWord",
            "description": "待检查变化和边沿触发的输入值"
        }
    ],
    "output": [
        {
            "name": "hasChanged",
            "type": "Bool",
            "description": "为True时表示输入值已改变"
        },
        {
            "name": "hasRisingEdges",
            "type": "Bool",
            "description": "为True时表示输入值出现上升边沿"
        },
        {
            "name": "risingBits",
            "type": "DWord",
            "description": "上升边沿的位流，其中每个位表示相应位置的输入值是否发生了上升沿（1表示有上升沿，0表示无上升沿）"
        },
        {
            "name": "noOfRisingBits",
            "type": "USInt",
            "description": "输入值中的上升边沿数量"
        },
        {
            "name": "hasFallingEdges",
            "type": "Bool",
            "description": "为True时表示输入值出现下降边沿"
        },
        {
            "name": "fallingBits",
            "type": "DWord",
            "description": "下降边沿的位流，其中每个位表示相应位置的输入值是否发生了下降沿（1表示有下降沿，0表示无下降沿）"
        },
        {
            "name": "noOfFallingBits",
            "type": "USInt",
            "description": "输入值中的下降边沿数量"
        }
    ]
}
题目一输出:
FUNCTION_BLOCK "GetBitStates"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      value : DWord;
   END_VAR
   VAR_OUTPUT 
      hasChanged  : Bool;
      hasRisingEdges : Bool;
      risingBits  : DWord;
      noOfRisingBits  : USInt;
      hasFallingEdges  : Bool;
      fallingBits  : DWord;
      noOfFallingBits  : USInt;
   END_VAR
   VAR 
      statPreviousValue  : DWord;
   END_VAR
   VAR_TEMP 
      tempRisingResult : DWord;
      tempNoRisingBits : DWord;
      tempFallingResult : DWord;
      tempNoFallingBits : DWord;
   END_VAR
   VAR CONSTANT 
      ZERO_EDGES : DWord;
   END_VAR
BEGIN
	REGION PROGRAM LOGIC
	  #tempRisingResult := #value AND NOT #statPreviousValue;
	  #tempFallingResult := NOT #value AND #statPreviousValue;
	  #statPreviousValue := #value;
	  #tempNoRisingBits := #tempRisingResult;
	  #tempNoRisingBits := UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoRisingBits) - DWORD_TO_UDINT(SHR(IN := #tempNoRisingBits, N := 1) AND 16#55555555));
	  #tempNoRisingBits := UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoRisingBits & 16#33333333) + DWORD_TO_UDINT(SHR(IN := #tempNoRisingBits, N := 2) AND 16#33333333));
	  #tempNoRisingBits := SHR(IN := UDINT_TO_DWORD(DWORD_TO_UDINT(UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoRisingBits) + DWORD_TO_UDINT(SHR(IN := #tempNoRisingBits, N := 4))) AND 16#0F0F0F0F) * DWORD_TO_UDINT(16#01010101)), N := 24);
	  #tempNoFallingBits := #tempFallingResult;
	  #tempNoFallingBits := UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoFallingBits) - DWORD_TO_UDINT(SHR(IN := #tempNoFallingBits, N := 1) AND 16#55555555));
	  #tempNoFallingBits := UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoFallingBits & 16#33333333) + DWORD_TO_UDINT(SHR(IN := #tempNoFallingBits, N := 2) AND 16#33333333));
	  #tempNoFallingBits := SHR(IN := UDINT_TO_DWORD(DWORD_TO_UDINT(UDINT_TO_DWORD(DWORD_TO_UDINT(#tempNoFallingBits) + DWORD_TO_UDINT(SHR(IN := #tempNoFallingBits, N := 4))) AND 16#0F0F0F0F) * DWORD_TO_UDINT(16#01010101)), N := 24);
	END_REGION PROGRAM LOGIC
	REGION OUTPUTS
	  #hasChanged := (#tempRisingResult > #ZERO_EDGES) OR (#tempFallingResult > #ZERO_EDGES);
	  #hasRisingEdges := #tempRisingResult > #ZERO_EDGES;
	  #risingBits := #tempRisingResult;
	  #noOfRisingBits := DWORD_TO_USINT(#tempNoRisingBits);
	  #hasFallingEdges := #tempFallingResult > #ZERO_EDGES;
	  #fallingBits := #tempFallingResult;
	  #noOfFallingBits := DWORD_TO_USINT(#tempNoFallingBits);
	  ENO := FALSE;
	END_REGION OUTPUTS
END_FUNCTION_BLOCK
题目二输入:
{
    "title": "数据类型为DTL的日期时间转换为字符串",
    "description": "编写一个函数FC，该函数能够将数据类型为DTL的日期时间值转换为字符串，并按照自定义的分隔符输出。转换后的字符串格式应为YYYY<分隔符>MM<分隔符>DD<分隔符>HH:mm:ss.nnnnnnnn，其中<分隔符>为函数参数指定的字符。这里HH代表小时（24小时制），mm代表分钟，ss代表秒，nnnnnnnn代表纳秒。注意，分隔符不应用于时分秒纳秒之间。
示例：
假设输入的DTL日期时间为2023-09-17 12:34:56.123456789，自定义分隔符为-。
函数应返回字符串"2023-09-17 12:34:56.123456789"作为转换结果。",
    "type": "FUNCTION",
    "name": "DTLToString_ISO",
    "input": [
        {
            "name": "date",
            "type": "DTL",
            "description": "数据类型为DTL的日期"
        },
        {
            "name": "separator",
            "type": "Char",
            "description": "转换后的日期中年和月之间，以及月和日之间的分隔符"
        }
    ],
    "return_value": [
        {
            "type": "String",
            "description": "转换后的日期字符串"
        }
    ]
}
题目二输出:
FUNCTION "DTLToString_ISO" : String
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      "date"  : DTL;
      separator : Char;
   END_VAR
   VAR_TEMP 
      tempString : String;
      tempIndex : DInt;
   END_VAR
   VAR CONSTANT 
      CONVERT_SIZE_YEAR : USInt := 4;
      CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND : USInt := 2;
      CONVERT_SIZE_NANOSECOND : USInt := 9;
      CONVERT_PRECISION : USInt := 0;
      CONVERT_FORMAT_TO_STRING : Word := 16#0000;
      CONVERT_START_POSITION_YEAR : UInt := 1;
      CONVERT_START_POSITION_MONTH : UInt := 6;
      CONVERT_START_POSITION_DAY : UInt := 9;
      CONVERT_START_POSITION_HOUR : UInt := 12;
      CONVERT_START_POSITION_MINUTE : UInt := 15;
      CONVERT_START_POSITION_SECOND : UInt := 18;
      CONVERT_START_POSITION_NANOSECOND : UInt := 21;
      SEPARATOR_POSITION_YEAR_MONTH : UInt := 5;
      SEPARATOR_POSITION_MONTH_DAY : UInt := 8;
      SEPARATOR_POSITION_HOUR_MINUTE : UInt := 14;
      SEPARATOR_POSITION_MINUTE_SECOND : UInt := 17;
      SEPARATOR_POSITION_SECOND_NANOSECOND : UInt := 20;
      SEPARATOR_NANOSECOND : Char := '.';
      SEPARATOR_TIME : Char := ':';
      SEPARATOR_DATE : Char := '-';
      REPLACE_NANOSECOND_COUNT : DInt := 8;
   END_VAR
BEGIN
	REGION INITIALISATION
	  #tempString := '';
	END_REGION
	REGION CONVERTER
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.YEAR,
	           P      := #CONVERT_START_POSITION_YEAR,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_YEAR,
	           OUT    => #tempString);    
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.MONTH,
	           P      := #CONVERT_START_POSITION_MONTH,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND,
	           OUT    => #tempString);     
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.DAY,
	           P      := #CONVERT_START_POSITION_DAY,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND,
	           OUT    => #tempString);     
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.HOUR,
	           P      := #CONVERT_START_POSITION_HOUR,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND,
	           OUT    => #tempString);     
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.MINUTE,
	           P      := #CONVERT_START_POSITION_MINUTE,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND,
	           OUT    => #tempString);     
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.SECOND,
	           P      := #CONVERT_START_POSITION_SECOND,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_MONTH_DAY_HOUR_MINUTE_SECOND,
	           OUT    => #tempString);     
	  VAL_STRG(FORMAT := #CONVERT_FORMAT_TO_STRING,
	           IN     := #date.NANOSECOND,
	           P      := #CONVERT_START_POSITION_NANOSECOND,
	           PREC   := #CONVERT_PRECISION,
	           SIZE   := #CONVERT_SIZE_NANOSECOND,
	           OUT    => #tempString);     
	  IF #separator = '' THEN
	    #tempString[#SEPARATOR_POSITION_YEAR_MONTH] := #SEPARATOR_DATE;
	    #tempString[#SEPARATOR_POSITION_MONTH_DAY] := #SEPARATOR_DATE;
	  ELSE
	    #tempString[#SEPARATOR_POSITION_YEAR_MONTH] := #separator;
	    #tempString[#SEPARATOR_POSITION_MONTH_DAY] := #separator;
	  END_IF;
	  #tempString[#SEPARATOR_POSITION_HOUR_MINUTE] := #SEPARATOR_TIME;
	  #tempString[#SEPARATOR_POSITION_MINUTE_SECOND] := #SEPARATOR_TIME;
	  #tempString[#SEPARATOR_POSITION_SECOND_NANOSECOND] := #SEPARATOR_NANOSECOND;
	  IF (#tempString[#CONVERT_START_POSITION_MONTH] = ' ') THEN
	    #tempString[#CONVERT_START_POSITION_MONTH] := '0';
	  END_IF;
	  IF (#tempString[#CONVERT_START_POSITION_DAY] = ' ') THEN
	    #tempString[#CONVERT_START_POSITION_DAY] := '0';
	  END_IF;
	  IF (#tempString[#CONVERT_START_POSITION_HOUR] = ' ') THEN
	    #tempString[#CONVERT_START_POSITION_HOUR] := '0';
	  END_IF;
	  IF (#tempString[#CONVERT_START_POSITION_MINUTE] = ' ') THEN
	    #tempString[#CONVERT_START_POSITION_MINUTE] := '0';
	  END_IF;
	  IF (#tempString[#CONVERT_START_POSITION_SECOND] = ' ') THEN
	    #tempString[#CONVERT_START_POSITION_SECOND] := '0';
	  END_IF;
	  FOR #tempIndex := 0 TO #REPLACE_NANOSECOND_COUNT DO
	    IF (#tempString[UINT_TO_SINT(#CONVERT_START_POSITION_NANOSECOND) + #tempIndex] = ' ') THEN
	      #tempString[UINT_TO_SINT(#CONVERT_START_POSITION_NANOSECOND) + #tempIndex] := '0';
	    ELSE
	      EXIT;
	    END_IF;
	  END_FOR;
	END_REGION
	REGION OUTPUTS
	  #DTLToString_ISO := #tempString;
	  ENO := TRUE;
	END_REGION
END_FUNCTION
题目三输入:
{
    "title": "从字符数组中截取字符串",
    "description": "编写一个函数FC，该函数能够根据给定的起始字符串和结束字符串，从字符数组中截取符合要求的子字符串。
1. 函数应遍历searchIn，查找textBefore首次出现的位置，然后查找随后出现的textAfter的位置。
2. 如果找到了textBefore和textAfter，函数应截取这两个边界之间的字符串（不包括边界字符串本身），并返回这个子字符串。
3. 如果textBefore或textAfter在searchIn中不存在，函数应返回特定的状态代码。
status参数表示程序的执行状态：
- 16#0000：执行成功
- 16#8200：输入参数searchIn不是字符数组或字节数组
返回值表示查找的结果：
- 16#0000：查找成功，头部字符和尾部字符均已找到
- 16#9001：查找不成功，只找到了起始边界，未找到结束边界
- 16#9002：查找不成功，起始边界未找到。
示例：
假设searchIn为"This is a [sample] string with [multiple] boundaries."，textBefore为"["，textAfter为"]"。函数应返回"sample"作为截取到的子字符串。",
    "type": "FUNCTION",
    "name": "ExtractStringFromCharArray",
    "input": [
        {
            "name": "textBefore",
            "type": "String",
            "description": "要截取的字符串的起始边界"
        },
        {
            "name": "textAfter",
            "type": "String",
            "description": "要截取的字符串的结束边界"
        }
    ],
    "output": [
        {
            "name": "extractedString",
            "type": "String",
            "description": "截取的字符串"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码，具体见说明"
        }
    ],
	"in/out": [
		{
            "name": "searchIn",
            "type": "Variant",
            "description": "要在其中进行搜索的字符或字节数组"
        }
	],
    "return_value": [
        {
            "type": "Word",
            "description": "状态代码，具体见说明"
        }
    ]
}
题目三输出:
FUNCTION "ExtractStringFromCharArray" : Word
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      textBefore : String;
      textAfter : String;
   END_VAR
   VAR_OUTPUT 
      extractedString : String;
      status : Word;
   END_VAR
   VAR_IN_OUT 
      searchIn : Variant;
   END_VAR
   VAR_TEMP 
      tempNumElements : UDInt;
      tempPosInArray : DInt;
      tempLenTextBefore : Int;
      tempPosTextBefore : DInt;
      tempLenTextAfter : Int;
      tempPosTextAfter : Int;
      tempString : String;
   END_VAR
   VAR CONSTANT 
      LEN_STRING : UInt := 254;
      STATUS_TEXT_FOUND : Word := 16#0000;
      WARNING_ONLY_START : Word := 16#9001;
      WARNING_NOTHING_FOUND : Word := 16#9002;
      STATUS_NO_ERROR : Word := 16#0000;
      ERR_NO_ARRAY : Word := 16#8200;
   END_VAR
BEGIN
	REGION Initialization
	  #tempPosTextBefore := 0;
	  #tempPosTextAfter := 0;
	  #tempPosInArray := 0;
	  #tempLenTextBefore := LEN(#textBefore);
	  #tempLenTextAfter := LEN(#textAfter);
	  #extractedString := '';
	  #status := #STATUS_NO_ERROR;
	  #ExtractStringFromCharArray := #WARNING_NOTHING_FOUND;
	  REGION Validation of inputs
	    IF TRUE
	      AND IS_ARRAY(#searchIn)
	      AND ((TypeOfElements(#searchIn) = Char) OR (TypeOfElements(#searchIn) = Byte))
	    THEN
	      #tempNumElements := CountOfElements(#searchIn);
	    ELSE
	      #status := #ERR_NO_ARRAY;
	      RETURN;
	    END_IF;
	  END_REGION Validation of inputs
	END_REGION Initialization
	REGION Process
	  REPEAT 
	    Chars_TO_Strg(Chars  := #searchIn,
	                  pChars := #tempPosInArray, 
	                  Cnt    := UDINT_TO_UINT(MIN(IN1 := #LEN_STRING, IN2 := #tempNumElements)),
	                  Strg   => #tempString);
	    #tempPosTextBefore := FIND(IN1 := #tempString, IN2 := #textBefore);
	    IF #tempPosTextBefore > 0 THEN
	      #tempPosInArray += #tempPosTextBefore + #tempLenTextBefore - 1;
	      Chars_TO_Strg(Chars  := #searchIn,
	                    pChars := #tempPosInArray, 
	                    Cnt    := UDINT_TO_UINT(MIN(IN1 := #LEN_STRING, IN2 := #tempNumElements)),
	                    Strg   => #tempString);
	      #tempPosTextAfter := FIND(IN1 := #tempString, IN2 := #textAfter);
	      IF #tempPosTextAfter > 0 THEN 
	        #extractedString := LEFT(IN := #tempString, L := #tempPosTextAfter - 1);
	        #ExtractStringFromCharArray := #STATUS_TEXT_FOUND;
	        EXIT;
	      ELSE 
	        #extractedString := #tempString;
	        #ExtractStringFromCharArray := #WARNING_ONLY_START;
	        EXIT;
	      END_IF;
	    ELSE
	      #tempPosInArray += UINT_TO_INT(#LEN_STRING) - #tempLenTextBefore;
	    END_IF;
	  UNTIL (#tempPosInArray > #tempNumElements) END_REPEAT;
	END_REGION Process
END_FUNCTION
题目四输入:
{
    "title": "FIFO先进先出队列",
    "description": "编写一个函数块FB，实现一个先进先出（FIFO）循环队列的功能，其中队列的最大长度和数据类型都是可变的。循环队列应能够支持以下操作：
1. 入队操作（enqueue）：在队列未满的情况下，将一个元素添加到队列的队尾。
2. 出队操作（dequeue）：在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。
3. 判断队列是否为空：检查队列中是否没有元素。
4. 判断队列是否已满：检查队列是否已达到最大容量。
5. 获取队列元素数量：返回队列中当前元素的数量。
状态代码：
16#0000：执行FB没有出错
16#8001：队列是空的
16#8002：队列是满的",
    "type": "FUNCTION_BLOCK",
    "name": "FIFO",
    "input": [
        {
            "name": "enqueue",
            "type": "Bool",
            "description": "入队操作，在队列未满的情况下，将一个元素添加到队列的队尾"
        },
        {
            "name": "dequeue",
            "type": "Bool",
            "description": "出队操作，在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。"
        },
        {
            "name": "reset",
            "type": "Bool",
            "description": "复位操作，复位头尾指针，元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。"
        },
        {
            "name": "clear",
            "type": "Bool",
            "description": "清除操作，复位头尾指针，队列将被清空并用初始值initialItem进行初始化。元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。"
        },
        {
            "name": "initialItem",
            "type": "Variant",
            "description": "用于初始化队列的值"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE:没有发生错误 TRUE:执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        },
        {
            "name": "elementCount",
            "type": "DInt",
            "description": "队列中元素的数量"
        },
        {
            "name": "isEmpty",
            "type": "Bool",
            "description": "当为TRUE时表示队列是空的"
        }
    ],
    "in/out": [
        {
            "name": "item",
            "type": "Variant",
            "description": "用于加入队列或从队列返回的值"
        },
        {
            "name": "buffer",
            "type": "Variant",
            "description": "用于作为队列的数组"
        }
    ]
}
题目四输出:
FUNCTION_BLOCK "FIFO"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      enqueue : Bool := FALSE;
      dequeue : Bool := FALSE;
      reset : Bool;
      clear : Bool;
      initialItem : Variant;
   END_VAR
   VAR_OUTPUT 
      error : Bool;
      status : Word;
      elementCount : DInt := 0;
      isEmpty : Bool := FALSE;
   END_VAR
   VAR_IN_OUT 
      item : Variant;
      buffer : Variant;
   END_VAR
   VAR 
      statEdgesMem : Struct
         enqueue : Bool;
         dequeue : Bool;
         clear : Bool;
      END_STRUCT;
      statFirstItemIndex : Int := -1;
      statNextEmptyItemIndex : Int := 0;
      statElementCount : DInt;
   END_VAR
   VAR_TEMP 
      tempEdges : Struct
         enqueue : Bool;
         dequeue : Bool;
         clear : Bool;
      END_STRUCT;
      tempInternalError : Int;
      tempNewFirstItemIndex : Int;
      tempNewNextEmptyItemIndex : Int;
      tempBufferSize : UDInt;
      tempCounter : Int;
   END_VAR
   VAR CONSTANT 
      BUFFER_IS_EMPTY : Int := -1;
      NO_INTERNAL_ERROR : Int := 0;
      BUFFER_INITIALIZED : Int := -1;
      EMPTY_INITIALIZED : Int := 0;
      INDEX_BEGINNING : Int := 0;
      COUNT_ELEMENTS : UDInt := 1;
      INCREMENT : Int := 1;
      BUFFER_SIZE_CORRECTION : UDInt := 1;
      COUNTER_LOWER_LIMIT : Int := 0;
      ZERO_ELEMENTS : DInt := 0;
      STATUS_NO_ERROR : Word := 16#0000;
      STATUS_NO_CURRENT_JOBS : Word := 16#7000;
      ERR_BUFFER_EMPTY : Word := 16#8001;
      ERR_BUFFER_FULL : Word := 16#8002;
      ERR_NO_ARRAY : Word := 16#8200;
      ERR_WRONG_TYPE_ITEM : Word := 16#8201;
      ERR_WRONG_TYPE_INITIAL_ITEM : Word := 16#8202;
      ERR_INDEX_IN_ARRAY_LIMITS_1 : Word := 16#8601;
      ERR_INDEX_IN_ARRAY_LIMITS_2 : Word := 16#8602;
      ERR_CLEAR_BUFFER : Word := 16#8610;
      ERR_RETURN_FIRST_ENTRY : Word := 16#8611;
      ERR_REPLACE_ITEM_BY_INIT_VALUE : Word := 16#8612;
      ERR_WRITE_ENTRY : Word := 16#8613;
   END_VAR
BEGIN
	REGION Block execution control
	    #tempEdges.enqueue := #enqueue AND NOT #statEdgesMem.enqueue;
	    #tempEdges.dequeue := #dequeue AND NOT #statEdgesMem.dequeue;
	    #tempEdges.clear := #clear AND NOT #statEdgesMem.clear;
	    #statEdgesMem.enqueue := #enqueue;
	    #statEdgesMem.dequeue := #dequeue;
	    #statEdgesMem.clear := #clear;
	    IF NOT (#enqueue OR #dequeue OR #reset OR #clear) THEN
	        #error := false;
	        #status := #STATUS_NO_CURRENT_JOBS;
	        RETURN;
	    END_IF;
	END_REGION
	REGION Validation of inputs
	    IF IS_ARRAY(#buffer) THEN
	        #tempBufferSize := CountOfElements(#buffer);
	    ELSE
	        #error := true;
	        #status := #ERR_NO_ARRAY;
	        RETURN;
	    END_IF;
	    IF (TypeOf(#item) <> TypeOfElements(#buffer)) THEN
	        #error := true;
	        #status := #ERR_WRONG_TYPE_ITEM;
	        RETURN;
	    END_IF;
	    IF (TypeOf(#item) <> TypeOf(#initialItem)) THEN
	        #error := true;
	        #status := #ERR_WRONG_TYPE_INITIAL_ITEM;
	        RETURN;
	    END_IF;
	    IF (#statNextEmptyItemIndex >= #tempBufferSize) THEN
	        #error := true;
	        #status := #ERR_INDEX_IN_ARRAY_LIMITS_1;
	        RETURN;
	    ELSIF (#statFirstItemIndex >= #tempBufferSize) THEN
	        #error := true;
	        #status := #ERR_INDEX_IN_ARRAY_LIMITS_2;
	        RETURN;
	    END_IF;
	    IF #reset THEN
	        #statFirstItemIndex := #BUFFER_INITIALIZED;
	        #statNextEmptyItemIndex := #EMPTY_INITIALIZED;
	        #statElementCount := #EMPTY_INITIALIZED;
	        #elementCount := #EMPTY_INITIALIZED;
	        #isEmpty := true;
	        RETURN;
	    END_IF;
	    IF #tempEdges.clear THEN
	        FOR #tempCounter := #COUNTER_LOWER_LIMIT TO UDINT_TO_INT(#tempBufferSize - #BUFFER_SIZE_CORRECTION) DO
	            #tempInternalError := MOVE_BLK_VARIANT(SRC := #initialItem,
	                                                   COUNT := #COUNT_ELEMENTS,
	                                                   SRC_INDEX := #INDEX_BEGINNING,
	                                                   DEST_INDEX := #tempCounter,
	                                                   DEST => #buffer);
	        END_FOR;
	        IF (#tempInternalError <> #NO_INTERNAL_ERROR) THEN
	            #error := true;
	            #status := #ERR_CLEAR_BUFFER;
	        END_IF;
	        #statFirstItemIndex := #BUFFER_INITIALIZED;
	        #statNextEmptyItemIndex := #EMPTY_INITIALIZED;
	        #statElementCount := #EMPTY_INITIALIZED;
	        #elementCount := #EMPTY_INITIALIZED;
	        #isEmpty := true;
	        RETURN;
	    END_IF;
	END_REGION
	REGION FIFO algorithm  
	    IF #tempEdges.dequeue THEN
	        REGION dequeue
	            IF (#statFirstItemIndex = #BUFFER_IS_EMPTY) THEN
	                #error := true;
	                #status := #ERR_BUFFER_EMPTY;
	                RETURN;
	            END_IF;
	            #tempInternalError := MOVE_BLK_VARIANT(SRC := #buffer,
	                                                   COUNT := #COUNT_ELEMENTS,
	                                                   SRC_INDEX := #statFirstItemIndex,
	                                                   DEST_INDEX := #INDEX_BEGINNING,
	                                                   DEST => #item);
	            IF (#tempInternalError <> #NO_INTERNAL_ERROR) THEN
	                #error := true;
	                #status := #ERR_RETURN_FIRST_ENTRY;
	                RETURN;
	            END_IF;
	            #tempInternalError := MOVE_BLK_VARIANT(SRC := #initialItem,
	                                                   COUNT := #COUNT_ELEMENTS,
	                                                   SRC_INDEX := #INDEX_BEGINNING,
	                                                   DEST_INDEX := #statFirstItemIndex,
	                                                   DEST => #buffer);
	            IF (#tempInternalError <> #NO_INTERNAL_ERROR) THEN
	                #error := true;
	                #status := #ERR_REPLACE_ITEM_BY_INIT_VALUE;
	                RETURN;
	            END_IF;
	            #tempNewFirstItemIndex := #statFirstItemIndex + #INCREMENT;
	            #tempNewFirstItemIndex := #tempNewFirstItemIndex MOD UDINT_TO_INT(#tempBufferSize);
	            IF (#statNextEmptyItemIndex = #tempNewFirstItemIndex) THEN
	                #statFirstItemIndex := #BUFFER_INITIALIZED;
	                #statNextEmptyItemIndex := #EMPTY_INITIALIZED;
	            ELSE
	                #statFirstItemIndex := #tempNewFirstItemIndex;
	            END_IF;
	            #statElementCount -= #INCREMENT;
	        END_REGION dequeue
	    ELSIF #tempEdges.enqueue THEN
	        REGION enqueue
	            IF (#statNextEmptyItemIndex = #statFirstItemIndex) THEN
	                #error := true;
	                #status := #ERR_BUFFER_FULL;
	                RETURN;
	            END_IF;
	            #tempInternalError := MOVE_BLK_VARIANT(SRC := #item,
	                                                   COUNT := #COUNT_ELEMENTS,
	                                                   SRC_INDEX := #INDEX_BEGINNING,
	                                                   DEST_INDEX := #statNextEmptyItemIndex,
	                                                   DEST => #buffer);
	            IF (#tempInternalError <> #NO_INTERNAL_ERROR) THEN
	                #error := true;
	                #status := #ERR_WRITE_ENTRY;
	                RETURN;
	            END_IF;
	            #tempNewNextEmptyItemIndex := (#statNextEmptyItemIndex + #INCREMENT) MOD UDINT_TO_INT(#tempBufferSize);
	            #statNextEmptyItemIndex := #tempNewNextEmptyItemIndex;
	            IF (#statFirstItemIndex = #BUFFER_INITIALIZED) THEN
	                #statFirstItemIndex := #INDEX_BEGINNING;
	            END_IF;
	            #statElementCount += #INCREMENT;
	        END_REGION enqueue
	    END_IF;
	END_REGION
	REGION Writing to outputs
	    #elementCount := #statElementCount;
	    #isEmpty := #statElementCount <= #ZERO_ELEMENTS;
	    #error := false;
	    #status := #STATUS_NO_ERROR;
	    ENO := TRUE;
	END_REGION
END_FUNCTION_BLOCK
题目五输入:
{
    "title": "计算移动平均值",
    "description": "编写一个函数块FB，该函数块计算并更新一个移动算术平均值。移动算术平均值是一种在连续数据点上进行平均的方法，其中每个新的数据点都会替换掉最旧的数据点，然后重新计算平均值。
1. cyclicExecution为TRUE时，每个扫描周期自动读取一次新数据value，并更新移动平均值average。
2. 提供外部触发信号trigger，当触发上升沿时，立即读取一次新数据并更新移动平均值。
3. 提供复位功能reset，当复位信号为TRUE时，重置移动平均值计算。如果窗口大小小于1或大于100，则输出错误状态和状态代码。
status参数表示程序的执行状态：
- 16#0000：执行成功
- 16#8200：窗口长度设置错误，请设置一个介于1到100之间的值。",
    "type": "FUNCTION_BLOCK",
    "name": "FloatingAverage",
    "input": [
        {
            "name": "cyclicExecution",
            "type": "Bool",
            "description": "为TRUE时，周期性读取，trigger不起作用"
        },
        {
            "name": "trigger",
            "type": "Bool",
            "description": "外部触发信号，每次上升沿读取value"
        },
        {
            "name": "value",
            "type": "LReal",
            "description": "新读取的数据值"
        },
        {
            "name": "windowSize",
            "type": "Int",
            "description": "移动平均值的窗口大小，要求范围在1到100之间"
        },
        {
            "name": "reset",
            "type": "Bool",
            "description": "复位信号，当为TRUE时重置移动平均值计算"
        }
    ],
    "output": [
        {
            "name": "average",
            "type": "LReal",
            "description": "移动平均值"
        },
        {
            "name": "windowSizeReached",
            "type": "Bool",
            "description": "FALSE:尚未达到最大窗口宽度 TRUE:已经达到最大窗口宽度"
        },
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE:没有发生错误 TRUE:执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ]
}
题目五输出:
FUNCTION_BLOCK "FloatingAverage"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      cyclicExecution : Bool := false;
      trigger : Bool;
      value : LReal;
      windowSize : Int := 100;
      reset : Bool;
   END_VAR
   VAR_OUTPUT 
      average  : LReal;
      windowSizeReached  : Bool;
      error  : Bool;
      status  : Word;
   END_VAR
   VAR 
      statValues  : Array[#ZERO_INT..#MAX_WINDOW_SIZE] of LReal;
      statValuesSum  : LReal := 0.0;
      statArithmeticAverage  : LReal := 0.0;
      statWindowSizeOld  : Int := 0;
      statCounter  : Int := 0;
      statwindowSizeReached  : Bool;
      statTriggerOld  : Bool := false;
   END_VAR
   VAR_TEMP 
      tempValue : LReal;
      tempIndex : Int;
      tempTriggerEdge : Bool;
   END_VAR
   VAR CONSTANT 
      ZERO_INT : Int := 0;
      ZERO_LREAL : LReal := 0.0;
      MAX_WINDOW_SIZE : Int := 100;
      INCREMENT : Int := 1;
      STATUS_FINISHED_NO_ERROR : Word := 16#0000;
      ERR_WRONG_WINDOW_SIZE : Word := 16#8200;
   END_VAR
BEGIN
	REGION Initialization and input data processing
	  #tempValue := #value;
	  #tempTriggerEdge := #trigger AND NOT #statTriggerOld;
	  #statTriggerOld := #trigger;
	  IF #reset OR (#windowSize <> #statWindowSizeOld) THEN
	    #statWindowSizeOld := #windowSize;
	    #statCounter := #ZERO_INT;
	    #statValuesSum := #ZERO_LREAL;
	    #statArithmeticAverage := #ZERO_LREAL;
	    #average := #ZERO_LREAL;
	    #windowSizeReached := FALSE;
	    #statwindowSizeReached := FALSE;
	    #error := false;
	    #status := #STATUS_FINISHED_NO_ERROR;
	    RETURN;
	  ELSIF (#windowSize <= #ZERO_INT) OR (#windowSize > #MAX_WINDOW_SIZE) THEN
	    #statWindowSizeOld := #windowSize;
	    #statCounter := #ZERO_INT;
	    #statValuesSum := #ZERO_LREAL;
	    #statArithmeticAverage := #ZERO_LREAL;
	    #average := #ZERO_LREAL;
	    #statwindowSizeReached := FALSE;
	    #windowSizeReached := FALSE;
	    #error := TRUE;
	    #status := #ERR_WRONG_WINDOW_SIZE; 
	    RETURN;
	  END_IF;
	END_REGION
	REGION Floating average calculation
	  IF #cyclicExecution OR #tempTriggerEdge THEN
	    #tempIndex := #statCounter MOD #windowSize;
	    IF (#statCounter < #windowSize) THEN
	      #statValuesSum += #tempValue;
	      #statValues[#tempIndex] := #tempValue;
	      #statCounter += #INCREMENT;
	      #statArithmeticAverage := #statValuesSum / #statCounter;
	    ELSE
	      #statwindowSizeReached := TRUE;
	      #statValuesSum += #tempValue - #statValues[#tempIndex];
	      #statValues[#tempIndex] := #tempValue;
	      #statArithmeticAverage := #statValuesSum / #windowSize;
	      IF (#tempIndex = #ZERO_INT) THEN
	        #statCounter := #windowSize + #INCREMENT;
	      ELSE
	        #statCounter += #INCREMENT;
	      END_IF;
	    END_IF;
	  END_IF;
	END_REGION
	REGION Outputs
	  #average := #statArithmeticAverage;
	  #windowSizeReached := #statwindowSizeReached;
	  #error := FALSE;
	  #status := #STATUS_FINISHED_NO_ERROR;
	  ENO := TRUE;
	END_REGION
END_FUNCTION_BLOCK
题目六输入:
{
    "title": "积分功能",
    "description": "编写一个函数块FB，该函数块实现输入信号的积分功能，并带有启动和复位功能。积分是对输入信号随时间的累积求和，通常用于计算流量、位移等物理量的累积值。启动功能用于开始积分计算，而复位功能用于将积分值重置为零。
当读取系统时间出错时，则输出错误状态和错误代码。
状态代码：
16#0000：执行FB没有出错
16#8600：读取系统时间错误",
    "type": "FUNCTION_BLOCK",
    "name": "Integration",
    "input": [
        {
            "name": "enable",
            "type": "Bool",
            "description": "启动信号，当该信号为TRUE时，启用积分计算；如果为FALSE，积分计算将停止，integral输出将显示最后一次计算的值。"
        },
        {
            "name": "value",
            "type": "LReal",
            "description": "需要积分的输入信号值"
        },
        {
            "name": "reset",
            "type": "Bool",
            "description": "复位信号，当该信号为TRUE时，将积分值重置为零"
        }
    ],
    "output": [
        {
            "name": "integral",
            "type": "LReal",
            "description": "积分值"
        },
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ]
}
题目六输出:
FUNCTION_BLOCK "Integration"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      enable : Bool;
      value : LReal;
      reset : Bool;
   END_VAR
   VAR_OUTPUT 
      integral : LReal;
      error : Bool;
      status : Word;
   END_VAR
   VAR 
      statLastTime  : DTL;
      statInputOldValue : LReal;
      statIntegral : LReal;
   END_VAR
   VAR_TEMP 
      tempSysTime  : DTL;
      tempTimeDiffrence : LReal;
      tempCalculation : LReal;
      tempRetval : Word;
   END_VAR
   VAR CONSTANT 
      CLEAR_TIME  : DTL;
      SECOND_IN_MS : LReal := 1000.0;
      DIVIDE_BY_TWO : LReal := 2.0;
      ZERO : LReal := 0.0;
      STATUS_EXECUTION_FINISHED_NO_ERROR : Word := 16#0000;
      SUB_STATUS_NO_ERROR : Word := 16#0000;
      ERR_READ_SYS_TIME : Word := 16#8600;
   END_VAR
BEGIN
	REGION Reset the function
	    IF #reset THEN
	        #statInputOldValue := #ZERO;
	        #statIntegral := #ZERO;
	        #statLastTime := #CLEAR_TIME;
	        #integral := #ZERO;
	        #error := false;
	        #status := #STATUS_EXECUTION_FINISHED_NO_ERROR;
	        RETURN;
	    END_IF;
	END_REGION Reset the function
	REGION Enable/Disable integral calculation
	    IF NOT #enable THEN
	        #statInputOldValue := #ZERO;
	        #statLastTime := #CLEAR_TIME;
	        #integral := #statIntegral;
	        #error := false;
	        #status := #STATUS_EXECUTION_FINISHED_NO_ERROR;
	        RETURN;
	    END_IF;
	END_REGION Enable/Disable integral calculation
	REGION Get system time
	    #tempRetval := INT_TO_WORD(RD_SYS_T(OUT => #tempSysTime));
	    IF (#tempRetval > #SUB_STATUS_NO_ERROR) THEN
	        #integral := #statIntegral;
	        #error := TRUE;
	        #status := #ERR_READ_SYS_TIME;
	        RETURN;
	    END_IF;
	END_REGION
	REGION Calculating the integral
	    #tempTimeDiffrence := DINT_TO_REAL(TIME_TO_DINT(T_DIFF(IN1 := #tempSysTime, IN2 := #statLastTime))) / #SECOND_IN_MS;
	    #statLastTime := #tempSysTime;
	    #tempCalculation := (#value + #statInputOldValue) * #tempTimeDiffrence / #DIVIDE_BY_TWO;
	    #statIntegral += #tempCalculation;
	    #statInputOldValue := #value;
	END_REGION Calculating the integral
	REGION Write outputs
	    #integral := #statIntegral;
	    #error := false;
	    #status := #STATUS_EXECUTION_FINISHED_NO_ERROR;
	    ENO := TRUE;
	END_REGION Write outputs
END_FUNCTION_BLOCK
题目七输入:
{
    "title": "灯控程序",
    "description": "编写一个函数块FB，实现一个灯控功能。
某控制台有3个指示灯，要求通过3个按钮开关进行控制。
1. 输入参数#button1~#button3表示3个按钮开关，输出参数#greenLight、#redLight、#yellowLight表示指示灯。
2. 当#button1=0时，表示手动模式，指示灯根据#button2和#button3的操作组合进行不同状态显示：
   - 当#button2和#button3都为0时，所有指示灯熄灭（#greenLight、#redLight、#yellowLight都为0）。
   - 当#button2为1且#button3为0时，#greenLight常亮，并且#redLight以0.5Hz的频率闪烁，即1秒灭，1秒亮。
   - 当#button2为0且#button3为1时，#redLight常亮，并且#yellowLight以1Hz的频率闪烁，即1秒灭，1秒亮。
   - 当#button2和#button3都为1时，#yellowLight常亮，并且#greenLight以1Hz的频率闪烁，即1秒灭，1秒亮。
3. 当#button1=1时，表示自动模式，指示灯自动按照如下说明循环执行：
   - 首先#greenLight亮，保持1秒。
   - 然后#greenLight熄灭，#redLight亮，保持1秒。
   - 然后#redLight熄灭，#yellowLight亮，保持1秒。
   - 然后回到初始状态#greenLight亮，保持1秒，如此循环。",
    "type": "FUNCTION_BLOCK",
    "name": "LightsControl",
    "input": [
        {
            "name": "button1",
            "type": "Bool",
            "description": "按钮1"
        },
        {
            "name": "button2",
            "type": "Bool",
            "description": "按钮2"
        },
        {
            "name": "button3",
            "type": "Bool",
            "description": "按钮3"
        }
    ],
    "output": [
        {
            "name": "greenLight",
            "type": "Bool",
            "description": "绿灯"
        },
        {
            "name": "redLight",
            "type": "Bool",
            "description": "红灯"
        },
        {
            "name": "yellowLight",
            "type": "Bool",
            "description": "黄灯"
        }
    ]
}
题目七输出:
FUNCTION_BLOCK "LightsControl"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      button1 : Bool;
      button2 : Bool;
      button3 : Bool;
   END_VAR
   VAR_OUTPUT 
      greenLight : Bool;
      redLight : Bool;
      yellowLight : Bool;
   END_VAR
   VAR 
      CycleStep : Int := 0;
      ManModeTimer1 : TON_TIME;
      ManModeTimer2 : TON_TIME;
      AutoModeTimer : TON_TIME;
   END_VAR
BEGIN
	    IF #button1 = FALSE THEN
	        #ManModeTimer1(IN := #ManModeTimer2.Q,
	                       PT := t#1s);
	        #ManModeTimer2(IN := NOT #ManModeTimer1.Q,
	                       PT := t#1s);
	        IF #button2 AND NOT #button3 THEN
	            #greenLight := TRUE;
	            #redLight := #ManModeTimer2.Q;
	            #yellowLight := FALSE;
	        ELSIF NOT #button2 AND #button3 THEN
	            #redLight := TRUE;
	            #yellowLight := #ManModeTimer2.Q;
	            #greenLight := FALSE;
	        ELSIF #button2 AND #button3 THEN
	            #yellowLight := TRUE;
	            #greenLight := #ManModeTimer2.Q;
	            #redLight := FALSE;
	        ELSE
	            #greenLight := FALSE;
	            #redLight := FALSE;
	            #yellowLight := FALSE;
	        END_IF;
	    ELSE
	        #AutoModeTimer(IN := TRUE,
	                       PT := T#1s);
	        CASE #CycleStep OF
	            0:
	                #greenLight := TRUE;
	                #redLight := FALSE;
	                #yellowLight := FALSE;
	                IF #AutoModeTimer.Q THEN
	                    #CycleStep := 1;
	                    #AutoModeTimer(IN := FALSE,
	                                   PT := T#1s);
	                END_IF;
	            1:
	                #greenLight := FALSE;
	                #redLight := TRUE;
	                #yellowLight := FALSE;
	                IF #AutoModeTimer.Q THEN
	                    #CycleStep := 2;
	                    #AutoModeTimer(IN := FALSE,
	                                   PT := T#1s);
	                END_IF;
	            2:
	                #greenLight := FALSE;
	                #redLight := FALSE;
	                #yellowLight := TRUE;
	                IF #AutoModeTimer.Q THEN
	                    #CycleStep := 0;
	                    #AutoModeTimer(IN := FALSE,
	                                   PT := T#1s);
	                END_IF;
	        END_CASE;
	    END_IF;
END_FUNCTION_BLOCK
题目八输入:
{
    "title": "矩阵加法",
    "description": "编写一个函数FC，实现两个矩阵的加法功能。
该函数接受两个可变长度的二维浮点数数组matrix1和matrix2作为输入参数。函数应检查两个输入矩阵以及用于返回结果的输出矩阵是否具有相同的行数和列数，如果不相同，则返回错误状态和特定的错误代码。
状态代码：
16#0000：执行FB没有出错
16#8200：第一矩阵数组行的下界值与第二矩阵行的下界值不同
16#8201：第一矩阵数组行的下界值与结果矩阵行的下界值不同
16#8202：第一矩阵数组列的下界值与第二矩阵列的下界值不同
16#8203：第一矩阵数组列的下界值与结果矩阵列的下界值不同
16#8204：第一矩阵数组行的上界值与第二矩阵行的上界值不同
16#8205：第一矩阵数组行的上界值与结果矩阵行的上界值不同
16#8206：第一矩阵数组列的上界值与第二矩阵列的上界值不同
16#8207：第一矩阵数组列的上界值与结果矩阵列的上界值不同",
    "type": "FUNCTION",
    "name": "MatrixAddition",
    "input": [
        {
            "name": "matrix1",
            "type": "Array[*, *] of LReal",
            "description": "第一矩阵"
        },
        {
            "name": "matrix2",
            "type": "Array[*, *] of LReal",
            "description": "第二矩阵"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "in/out": [
        {
            "name": "matrixResult",
            "type": "Array[*, *] of LReal",
            "description": "存放计算结果的矩阵"
        }
    ]
}
题目八输出:
FUNCTION "MatrixAddition" : Void
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      matrix1 : Array[*, *] of LReal;
      matrix2 : Array[*, *] of LReal;
   END_VAR
   VAR_OUTPUT 
      error : Bool;
      status : Word;
   END_VAR
   VAR_IN_OUT 
      matrixResult : Array[*, *] of LReal;
   END_VAR
   VAR_TEMP 
      tempMatrix1LowerBoundRows : DInt;
      tempMatrix1LowerBoundColumns : DInt;
      tempMatrix1UpperBoundRows : DInt;
      tempMatrix1UpperBoundColumns : DInt;
      tempMatrix2LowerBoundRows : DInt;
      tempMatrix2LowerBoundColumns : DInt;
      tempMatrix2UpperBoundRows : DInt;
      tempMatrix2UpperBoundColumns : DInt;
      tempResultMatrixLowerBoundRows : DInt;
      tempResultMatrixLowerBoundColumns : DInt;
      tempResultMatrixUpperBoundRows : DInt;
      tempResultMatrixUpperBoundColumns : DInt;
      tempCounterRows : DInt;
      tempCounterColumns : DInt;
   END_VAR
   VAR CONSTANT 
      ROWS : UInt := 1;
      COLUMNS : UInt := 2;
      STATUS_NO_ERROR : Word := 16#0000;
      ERR_MATR1_LOWBOUND_ROWS_MATR2_LOWBOUND_ROWS : Word := 16#8200;
      ERR_MATR1_LOWBOUND_ROWS_RESMATR_LOWBOUND_ROWS : Word := 16#8201;
      ERR_MATR1_LOWBOUND_COLUMNS_MATR2_LOWBOUND_COLUMNS : Word := 16#8202;
      ERR_MATR1_LOWBOUND_COLUMNS_RESMATR_LOWBOUND_COLUMNS : Word := 16#8203;
      ERR_MATR1_UPPBOUND_ROWS_MATR2_UPPBOUND_ROWS : Word := 16#8204;
      ERR_MATR1_UPPBOUND_ROWS_RESMATR_UPPBOUND_ROWS : Word := 16#8205;
      ERR_MATR1_UPPBOUND_COLUMNS_MATR2_UPPBOUND_COLUMNS : Word := 16#8206;
      ERR_MATR1_UPPBOUND_COLUMNS_RESMATR_UPPBOUND_COLUMNS : Word := 16#8207;
   END_VAR
BEGIN
	REGION Getting matrices size
	  #tempMatrix1LowerBoundRows := LOWER_BOUND(ARR := #matrix1, DIM := #ROWS);
	  #tempMatrix2LowerBoundRows := LOWER_BOUND(ARR := #matrix2, DIM := #ROWS);
	  #tempResultMatrixLowerBoundRows := LOWER_BOUND(ARR := #matrixResult, DIM := #ROWS);
	  #tempMatrix1LowerBoundColumns := LOWER_BOUND(ARR := #matrix1, DIM := #COLUMNS);
	  #tempMatrix2LowerBoundColumns := LOWER_BOUND(ARR := #matrix2, DIM := #COLUMNS);
	  #tempResultMatrixLowerBoundColumns := LOWER_BOUND(ARR := #matrixResult, DIM := #COLUMNS);
	  #tempMatrix1UpperBoundRows := UPPER_BOUND(ARR := #matrix1, DIM := #ROWS);
	  #tempMatrix2UpperBoundRows := UPPER_BOUND(ARR := #matrix2, DIM := #ROWS);
	  #tempResultMatrixUpperBoundRows := UPPER_BOUND(ARR := #matrixResult, DIM := #ROWS);
	  #tempMatrix1UpperBoundColumns := UPPER_BOUND(ARR := #matrix1, DIM := #COLUMNS);
	  #tempMatrix2UpperBoundColumns := UPPER_BOUND(ARR := #matrix2, DIM := #COLUMNS);
	  #tempResultMatrixUpperBoundColumns := UPPER_BOUND(ARR := #matrixResult, DIM := #COLUMNS);
	END_REGION
	REGION Error evaluation of matrixes dimentions
	  IF (#tempMatrix1LowerBoundRows <> #tempMatrix2LowerBoundRows) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_LOWBOUND_ROWS_MATR2_LOWBOUND_ROWS;
	    RETURN;
	  ELSIF (#tempMatrix1LowerBoundRows <> #tempResultMatrixLowerBoundRows) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_LOWBOUND_ROWS_RESMATR_LOWBOUND_ROWS;
	    RETURN;
	  ELSIF (#tempMatrix1LowerBoundColumns <> #tempMatrix2LowerBoundColumns) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_LOWBOUND_COLUMNS_MATR2_LOWBOUND_COLUMNS;
	    RETURN;
	  ELSIF (#tempMatrix1LowerBoundColumns <> #tempResultMatrixLowerBoundColumns) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_LOWBOUND_COLUMNS_RESMATR_LOWBOUND_COLUMNS;
	    RETURN;
	  END_IF;
	  IF (#tempMatrix1UpperBoundRows <> #tempMatrix2UpperBoundRows) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_UPPBOUND_ROWS_MATR2_UPPBOUND_ROWS;
	    RETURN;
	  ELSIF (#tempMatrix1UpperBoundRows <> #tempResultMatrixUpperBoundRows) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_UPPBOUND_ROWS_RESMATR_UPPBOUND_ROWS;
	    RETURN;
	  ELSIF (#tempMatrix1UpperBoundColumns <> #tempMatrix2UpperBoundColumns) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_UPPBOUND_COLUMNS_MATR2_UPPBOUND_COLUMNS;
	    RETURN;
	  ELSIF (#tempMatrix1UpperBoundColumns <> #tempResultMatrixUpperBoundColumns) THEN
	    #error := TRUE;
	    #status := #ERR_MATR1_UPPBOUND_COLUMNS_RESMATR_UPPBOUND_COLUMNS;
	    RETURN;
	  END_IF;
	END_REGION
	REGION Addition of the matrices and writting to output
	  FOR #tempCounterRows := #tempMatrix1LowerBoundRows TO #tempMatrix1UpperBoundRows DO
	    FOR #tempCounterColumns := #tempMatrix1LowerBoundColumns TO #tempMatrix1UpperBoundColumns DO
	      #matrixResult[#tempCounterRows, #tempCounterColumns] := #matrix1[#tempCounterRows, #tempCounterColumns] + #matrix2[#tempCounterRows, #tempCounterColumns];
	    END_FOR;
	  END_FOR;
	  #error := false;
	  #status := #STATUS_NO_ERROR;
	  ENO := TRUE;
	END_REGION
END_FUNCTION
题目九输入:
{
    "title": "随机数",
    "description": "编写一个函数FC，该函数使用PLC的时钟值在指定的范围内生成一个随机整数。
如果指定的范围不正确或读取系统时间出错，则输出错误状态和错误代码。
状态代码
16#0000：执行FB没有出错
16#8200：指定的范围不正确：minValue 大于 maxValue
16#8600：读取系统时间错误",
    "type": "FUNCTION",
    "name": "RandomRange_DInt",
    "input": [
        {
            "name": "minValue",
            "type": "DInt",
            "description": "随机数范围的最小值"
        },
        {
            "name": "maxValue",
            "type": "DInt",
            "description": "随机数范围的最大值"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "return_value": [
        {
            "type": "DInt",
            "description": "产生的随机数"
        }
    ]
}
题目九输出:
FUNCTION "RandomRange_DInt" : DInt
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      minValue : DInt;
      maxValue : DInt;
   END_VAR
   VAR_OUTPUT 
      error : Bool;
      status : Word;
   END_VAR
   VAR_TEMP 
      tempTime  : DTL;
      tempNanoSecondInDWord : DWord;
      tempTimeStatus : Word;
      tempRandomValue : DWord;
      tempNormReal : Real;
   END_VAR
   VAR CONSTANT 
      ZERO : DInt := 0;
      MAX_UDINT : UDInt := 4_294_967_295;
      SUB_STATUS_NO_ERROR : Word := 16#0000;
      STATUS_FINISHED_NO_ERROR : Word := 16#0000;
      ERR_MAX_LESS_MIN : Word := 16#8200;
      ERR_RD_SYS_T : Word := 16#8600;
   END_VAR
BEGIN
	REGION Validation
	    IF (#minValue > #maxValue) THEN
	        #error := true;
	        #status := #ERR_MAX_LESS_MIN;
	        #RandomRange_DInt := #ZERO;
	        RETURN;
	    END_IF;
	    #tempTimeStatus := INT_TO_WORD(RD_SYS_T(#tempTime));
	    IF (#tempTimeStatus <> #SUB_STATUS_NO_ERROR) THEN
	        #error := true;
	        #status := #ERR_RD_SYS_T;
	        #RandomRange_DInt := #ZERO;
	        RETURN;
	    END_IF;
	END_REGION
	REGION Calculating random number
	    #tempNanoSecondInDWord := UDINT_TO_DWORD(#tempTime.NANOSECOND);
	    #tempRandomValue.%B3 := #tempNanoSecondInDWord.%B0;
	    #tempRandomValue.%B2 := #tempNanoSecondInDWord.%B1;
	    #tempRandomValue.%B1 := #tempNanoSecondInDWord.%B2;
	    #tempRandomValue.%B0 := #tempNanoSecondInDWord.%B3;
	    #tempNormReal := UDINT_TO_REAL(DWORD_TO_UDINT(#tempRandomValue)) / UDINT_TO_REAL(#MAX_UDINT);
	    #RandomRange_DInt := REAL_TO_DINT((#tempNormReal * DINT_TO_REAL(#maxValue - #minValue) + DINT_TO_REAL(#minValue)));
	    #error := false;
	    #status := #STATUS_FINISHED_NO_ERROR;
	    ENO := TRUE;
	END_REGION
END_FUNCTION
题目十输入:
{
    "title": "查找最大最小值",
    "description": "编写一个函数FC，该函数能够接收一个可变长度的整数数组作为输入，并返回数组中的最大值和最小值以及他们所在数组的位置。
示例：
假设输入数组为array[1..5]=[5, 10, 2, 25, 1]，函数应返回最大值25，最小值1，最大值所在位置4，最小值所在位置5。",
    "type": "FUNCTION",
    "name": "SearchMinMax_DInt",
    "input": [
        {
            "name": "values",
            "type": "Array[*] of DInt",
            "description": "待查找的数组"
        }
    ],
    "output": [
        {
            "name": "minValue",
            "type": "DInt",
            "description": "数组中的最小值"
        },
        {
            "name": "minValueIndex",
            "type": "DInt",
            "description": "最小值在数组中的位置"
        },
        {
            "name": "maxValue",
            "type": "DInt",
            "description": "数组中的最大值"
        },
        {
            "name": "maxValueIndex",
            "type": "DInt",
            "description": "最大值在数组中的位置"
        }
    ]
}
题目十输出:
FUNCTION "SearchMinMax_DInt" : Void
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      values : Array[*] of DInt;
   END_VAR
   VAR_OUTPUT 
      minValue : DInt;
      minValueIndex : DInt;
      maxValue : DInt;
      maxValueIndex : DInt;
   END_VAR
   VAR_TEMP 
      tempArrayLowerBound : DInt;
      tempArrayUpperBound : DInt;
      tempCounter : DInt;
      tempArrayIndexMax : DInt;
      tempArrayIndexMin : DInt;
      tempActValue : DInt;
      tempMinValue : DInt;
      tempMaxValue : DInt;
   END_VAR
   VAR CONSTANT 
      START_FROM_SECOND_ELEMENT : Int := 1;
      DIMENSION_ONE : UInt := 1;
   END_VAR
BEGIN
	REGION Validation of inputs and outputs 
	  #tempArrayLowerBound := LOWER_BOUND(ARR := #values, DIM := #DIMENSION_ONE);
	  #tempArrayUpperBound := UPPER_BOUND(ARR := #values, DIM := #DIMENSION_ONE);
	END_REGION
	REGION Searching the array 
	  #tempMinValue := #tempMaxValue := #values[#tempArrayLowerBound];
	  #tempArrayIndexMin := #tempArrayIndexMax := #tempArrayLowerBound;
	  FOR #tempCounter := (#tempArrayLowerBound + #START_FROM_SECOND_ELEMENT) TO #tempArrayUpperBound DO
	    #tempActValue := #values[#tempCounter];
	    IF #tempActValue < #tempMinValue THEN
	      #tempMinValue := #tempActValue;
	      #tempArrayIndexMin := #tempCounter;
	    ELSIF #tempActValue > #tempMaxValue THEN
	      #tempMaxValue := #tempActValue;
	      #tempArrayIndexMax := #tempCounter;
	    END_IF;
	  END_FOR;
	END_REGION
	REGION Writting to outputs
	  #minValue := #values[#tempArrayIndexMin];
	  #maxValue := #values[#tempArrayIndexMax];
	  #minValueIndex := #tempArrayIndexMin;
	  #maxValueIndex := #tempArrayIndexMax;
	  ENO := TRUE;
	END_REGION
END_FUNCTION
题目十一输入:
{
    "title": "生成脉冲信号",
    "description": "编写一个函数块FB，该函数块生成一个周期性的信号，该信号在FALSE和TRUE之间变化。每个周期中TRUE状态的持续时间和FALSE状态的持续时间由给定的频率和脉冲间歇比决定。脉冲间歇比定义的是每个周期中TRUE状态的持续时间与FALSE状态的持续时间之比。
示例：
假设frequency为0.5Hz，pulsePauseRatio为3。这意味着每个周期是2秒，其中TRUE状态持续1.5秒，FALSE状态持续0.5秒。",
    "type": "FUNCTION_BLOCK",
    "name": "Frequency",
    "input": [
        {
            "name": "frequency",
            "type": "Real",
            "description": "以Hz为单位的时钟频率"
        },
        {
            "name": "pulsePauseRatio",
            "type": "Real",
            "description": "脉冲间歇比，定义为每个周期中TRUE状态的持续时间与FALSE状态的持续时间之比。例如，如果pulsePauseRatio为2，则TRUE状态的持续时间将是FALSE状态的两倍。"
        }
    ],
    "output": [
        {
            "name": "clock",
            "type": "Bool",
            "description": "脉冲输出"
        },
        {
            "name": "countdown",
            "type": "Time",
            "description": "当前状态的剩余时间"
        }
    ]
}
题目十一输出:
FUNCTION_BLOCK "Frequency"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      frequency : Real := 0.0;
      pulsePauseRatio : Real := 1.0;
   END_VAR
   VAR_OUTPUT 
      clock  : Bool;
      countdown  : Time;
   END_VAR
   VAR 
      instTofTimePulse  : TOF_TIME;
      instTofTimePause  : TOF_TIME;
      statFrequencyOld  : Real;
      statPulsePauseRatioOld : Real;
      statTimePulse  : Time;
      statTimePause  : Time;
   END_VAR
   VAR_TEMP 
      tempPulseRate : Real;
      tempPauseRate : Real;
      tempCountdown : Time;
   END_VAR
   VAR CONSTANT 
      ZERO : Real := 0.0;
      ZERO_TIME : Time := T#0ms;
      SECOND_IN_MS : Real := 1000.0;
      ONE : Real := 1.0;
   END_VAR
BEGIN
	REGION Calculation of settings and program execution
	  IF (#frequency <= #ZERO) OR (#pulsePauseRatio <= #ZERO) THEN
	    #clock := FALSE;
	    #tempCountdown := #ZERO_TIME;
	  ELSE
	    IF #statFrequencyOld <> #frequency OR #statPulsePauseRatioOld <> #pulsePauseRatio THEN
	      RESET_TIMER(TIMER := #instTofTimePause);
	      RESET_TIMER(TIMER := #instTofTimePulse);
	      #tempPulseRate := #pulsePauseRatio / (#pulsePauseRatio + #ONE); 
	      #tempPauseRate := #ONE - #tempPulseRate;                      
	      #statTimePulse := UDINT_TO_TIME(REAL_TO_UDINT((#SECOND_IN_MS * #tempPulseRate / #frequency))); 
	      #statTimePause := UDINT_TO_TIME(REAL_TO_UDINT((#SECOND_IN_MS * #tempPauseRate / #frequency))); 
	      #statFrequencyOld := #frequency;
	      #statPulsePauseRatioOld := #pulsePauseRatio;
	    END_IF;
	    #instTofTimePulse(IN := NOT #instTofTimePause.Q,
	                      PT := #statTimePulse);
	    #tempCountdown := #statTimePulse - #instTofTimePulse.ET;
	    #instTofTimePause(IN := #instTofTimePulse.Q,
	                      PT := #statTimePause);
	    IF #tempCountdown = #ZERO_TIME THEN
	      #tempCountdown := #statTimePause - #instTofTimePause.ET;
	    END_IF;
	  END_IF;
	END_REGION
	REGION Writing to outputs
	  #clock := #instTofTimePulse.Q;
	  #countdown := #tempCountdown;
	  ENO := TRUE;
	END_REGION
END_FUNCTION_BLOCK
题目十二输入:
{
    "title": "排序",
    "description": "编写一个函数块FB，实现一个可选的升序或降序排序功能。该函数块应接受一个可变长度的整数数组（最大长度为1000个元素）以及一个指示排序方向的参数（升序或降序），并将排序后的结果写回到原数组中。如果数组元素超过了1000或不超过1个，函数块应输出一个表示错误的状态和一个错误代码。状态代码：
16#0000：执行FB没有出错
16#8200：数组元素没超过1个
16#8201：数组元素超过了1000个",
    "type": "FUNCTION_BLOCK",
    "name": "ShellSort_DInt",
    "input": [
        {
            "name": "sortDirection",
            "type": "Bool",
            "description": "当为FALSE时表示升序排列，当为TRUE时表示降序排列"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "in/out": [
        {
            "name": "array",
            "type": "Array[*] of DInt",
            "description": "待排序的数组"
        }
    ]
}
题目十二输出:
FUNCTION_BLOCK "ShellSort_DInt"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      sortDirection : Bool;
   END_VAR
   VAR_OUTPUT 
      error : Bool;
      status  : Word;
   END_VAR
   VAR_IN_OUT 
      "array" : Array[*] of DInt;
   END_VAR
   VAR 
      tempArray : Array[1..#MAX_ARRAY_ELEMENTS] of DInt;
   END_VAR
   VAR_TEMP 
      tempLowerLimit : DInt;
      tempUpperLimit : DInt;
      tempNoOfElements : DInt;
      tempGap : DInt;
      tempLoopIndex : DInt;
      tempExchangeIndex : DInt;
      tempExchangeVariable : DInt;
      tempArrayOffset : DInt;
   END_VAR
   VAR CONSTANT 
      ARRAY_FIRST_DIMENSION : UInt := 1;
      ARRAY_START_INDEX : UInt := 1;
      SINGLE_ARRAY_ELEMENT : DInt := 1;
      GAP_INIT : Int := 1;
      GAP_THRESHOLD : Int := 1;
      GAP_RATIO : DInt := 3;
      INCREMENT : Int := 1;
      ELEMENTS_COUNT_CORRECTION : DInt := 1;
      MAX_ARRAY_ELEMENTS : Int := 1000;
      STATUS_NO_ERROR : Word := 16#0000;
      ERR_NO_ARRAY : Word := 16#8200;
      ERR_TOO_MANY_ELEMENTS : Word := 16#8201;
   END_VAR
BEGIN
	REGION Initialization and input data processing
	  #tempLowerLimit := LOWER_BOUND(ARR := #array, DIM := #ARRAY_FIRST_DIMENSION);
	  #tempUpperLimit := UPPER_BOUND(ARR := #array, DIM := #ARRAY_FIRST_DIMENSION);
	  #tempNoOfElements := #tempUpperLimit - #tempLowerLimit + #ELEMENTS_COUNT_CORRECTION;
	  #tempArrayOffset := - #tempLowerLimit + #ARRAY_START_INDEX;
	  IF #tempNoOfElements > #MAX_ARRAY_ELEMENTS THEN
	    #error := true;
	    #status := #ERR_TOO_MANY_ELEMENTS;
	    RETURN;
	  ELSIF #tempNoOfElements <= #SINGLE_ARRAY_ELEMENT THEN
	    #error := true;
	    #status := #ERR_NO_ARRAY;
	    RETURN;
	  END_IF;
	END_REGION
	REGION Sorting
	  FOR #tempLoopIndex := #tempLowerLimit TO #tempUpperLimit DO
	    #tempArray[#tempLoopIndex + #tempArrayOffset] := #array[#tempLoopIndex];
	  END_FOR;
	  REGION Shell sort algorithm
	    #tempGap := #GAP_INIT;
	    REPEAT
	      #tempGap := (#GAP_RATIO * #tempGap) + #INCREMENT;
	    UNTIL #tempGap > #tempNoOfElements END_REPEAT;
	    REPEAT
	      #tempGap := #tempGap / #GAP_RATIO;
	      FOR #tempLoopIndex := #tempGap + #INCREMENT TO #tempNoOfElements DO
	        #tempExchangeVariable := #tempArray[#tempLoopIndex];
	        #tempExchangeIndex := #tempLoopIndex;
	        IF #sortDirection THEN
	          WHILE ((#tempArray[#tempExchangeIndex - #tempGap] < #tempExchangeVariable)) DO
	            #tempArray[#tempExchangeIndex] := #tempArray[#tempExchangeIndex - #tempGap];
	            #tempExchangeIndex := #tempExchangeIndex - #tempGap;
	            IF (#tempExchangeIndex <= #tempGap) THEN
	              EXIT;
	            END_IF;
	          END_WHILE;
	        ELSE
	          WHILE ((#tempArray[#tempExchangeIndex - #tempGap] > #tempExchangeVariable)) DO
	            #tempArray[#tempExchangeIndex] := #tempArray[#tempExchangeIndex - #tempGap];
	            #tempExchangeIndex := #tempExchangeIndex - #tempGap;
	            IF (#tempExchangeIndex <= #tempGap) THEN
	              EXIT;
	            END_IF;
	          END_WHILE;
	        END_IF;
	        #tempArray[#tempExchangeIndex] := #tempExchangeVariable;
	      END_FOR;
	    UNTIL #tempGap <= #GAP_THRESHOLD END_REPEAT;
	  END_REGION
	  FOR #tempLoopIndex := #tempLowerLimit TO #tempUpperLimit DO
	    #array[#tempLoopIndex] := #tempArray[#tempLoopIndex + #tempArrayOffset];
	  END_FOR;
	  #error := false;
	  #status := #STATUS_NO_ERROR;
	  ENO := TRUE;
	END_REGION
END_FUNCTION_BLOCK
题目十三输入:
{
    "title": "特殊堆栈",
    "description": "编写一个函数块FB，实现一个特殊堆栈功能，在出栈时移除栈内的最小值。
1. 入栈操作：当新元素入栈时，首先检查栈是否为满。如果栈为满，则不进行任何操作。否则，将其添加到数组的栈顶位置，并更新栈顶位置。
2. 出栈操作：当执行出栈操作时，首先检查栈是否为空。如果栈为空，则不进行任何操作。否则，移除栈内的最小值，并返回该元素的值，同时更新栈顶位置。
状态代码：
16#0000：执行FB没有出错
16#8A04：堆栈是满的
16#8A05：堆栈是空的",
    "type": "FUNCTION_BLOCK",
    "name": "StackMin",
    "input": [
        {
            "name": "push",
            "type": "Bool",
            "description": "入栈操作，在栈未满的情况下，将一个元素添加到栈内"
        },
        {
            "name": "pop",
            "type": "Bool",
            "description": "出栈操作，在栈不空的情况下，从栈内移除最小值元素，并返回该元素的值。"
        },
        {
            "name": "reset",
            "type": "Bool",
            "description": "复位操作，栈顶位置将被重置。"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "in/out": [
        {
            "name": "item",
            "type": "Int",
            "description": "用于入栈或从栈内返回的值"
        },
        {
            "name": "stack",
            "type": "Array[0..3] of Int",
            "description": "用于作为栈的数组"
        }
    ]
}
题目十三输出:
FUNCTION_BLOCK "StackMin"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      push : Bool;   
      pop : Bool;   
      reset : Bool;   
   END_VAR
   VAR_OUTPUT 
      error : Bool;   
      status : Word;   
   END_VAR
   VAR_IN_OUT 
      item : Int;   
      stack : Array[0..3] of Int;   
   END_VAR
   VAR 
      statStackIndex : Int;   
      statMin : Int;
   END_VAR
   VAR_TEMP 
      tempStackSize : DInt;
      tempCount : Int;
   END_VAR
   VAR CONSTANT 
      STACK_FULL : Word := 16#8A04;   
      STACK_EMPTY : Word := 16#8A05;   
      NO_ERROR : Word := 16#0000;
   END_VAR
BEGIN
	REGION StackSize
	    #tempStackSize := 4;
	END_REGION
	REGION Push
	    IF #push = TRUE THEN
	        IF #statStackIndex >= #tempStackSize THEN             
	            #error := TRUE;
	            #status := #STACK_FULL;
	            RETURN;
	        END_IF;
	        #stack[#statStackIndex] := #item;                    
	        #statStackIndex += 1;                                
	    END_IF;
	END_REGION
	REGION Pop
	    IF #pop = TRUE THEN
	        IF #statStackIndex <= 0 THEN                          
	            #error := TRUE;
	            #status := #STACK_EMPTY;
	            RETURN;
	        END_IF;
	        #statMin := 0;
	        IF #statStackIndex>1 THEN
	            FOR #tempCount := 1 TO #statStackIndex - 1 DO
	                IF #stack[#tempCount] < #stack[#statMin] THEN
	                    #statMin := #tempCount;
	                END_IF;
	            END_FOR;
	        END_IF;
	        #item := #stack[#statMin];               
	        IF #statMin<>#statStackIndex-1 THEN
	            FOR #tempCount := #statMin TO #statStackIndex - 2 DO
	                #stack[#tempCount] := #stack[#tempCount + 1];
	            END_FOR;
	        END_IF;
	        #stack[#statStackIndex - 1] := 0;
	        #statStackIndex -= 1;                               
	    END_IF;
	END_REGION
	REGION Reset
	    IF #reset = TRUE THEN
	        #statStackIndex := 0;
	    END_IF;
	END_REGION
	#error := FALSE;
	#status := #NO_ERROR;
END_FUNCTION_BLOCK
题目十四输入:
{
    "title": "字符串转换为IP地址和端口号",
    "description": "在西门子PLC编程中，经常需要从用户输入或外部设备接收包含IP地址和端口号的字符串，并将其解析为相应的整数格式以便进行网络通信。
编写一个函数FC，用于将包含IP地址和可能包含端口号的字符串转换为整数形式的IP地址和端口号。字符串的格式应为"xxx.xxx.xxx.xxx[:port]"，其中xxx代表0-255之间的数字，port代表0-65535之间的端口号（可选）。如果字符串包含端口号，则同时返回端口号；如果不包含，则返回默认的端口号（比如0）。把转换后的IP地址和端口号返回给系统数据类型TADDR_Param结构体的相应位置。
函数应检查输入字符串是否符合"IP_ADDRESS:PORT"的格式要求，其中IP地址由四个用点分隔的0到255之间的整数组成，端口号为一个0到65535之间的整数。
如果字符串格式正确，函数应将其解析为四个字节的整数数组表示的IP地址和一个整数表示的端口号，并将这些值返回。
如果字符串格式不正确，函数应输出一个表示错误的状态和一个错误代码。
状态代码：
16#0000：执行FB没有出错
16#811x：IP地址含有过多字符，其中x表示出错的最低字节序号，例如，IP地址的第2个字节有错，则x=2
16#812x：IP地址字符串是空字符串，x表示的含义同上
16#813x：超过IP地址最大值（255），x表示的含义同上
16#8150：端口号字符过多
16#8151：端口号字符串为空
16#8152：超过端口号最大值（65535）",
    "type": "FUNCTION",
    "name": "StringToTaddr",
    "input": [
        {
            "name": "ipAddressString",
            "type": "String",
            "description": "输入的字符串"
        }
    ],
    "output": [
        {
            "name": "error",
            "type": "Bool",
            "description": "FALSE: 没有发生错误; TRUE: 执行FB时出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "return_value": [
        {
            "type": "TADDR_Param",
            "description": "转换后的IP地址和端口号"
        }
    ]
}
题目十四输出:
FUNCTION "StringToTaddr" : TADDR_Param
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      ipAddressString : String;
   END_VAR
   VAR_OUTPUT 
      error : Bool;
      status : Word;
   END_VAR
   VAR_TEMP 
      tempOctetIndex : Int;
      tempCharPosition : Int;
      tempAddressString : String;
      tempOctetString : String[#MAX_CHAR_FOR_IP_OCTET_NUMBER];
      tempNumber : UDInt;
      tempPortNumberIsSpecified : Bool;
      tempIpAdressTaddr  : TADDR_Param;
   END_VAR
   VAR CONSTANT 
      STATUS_FINISHED_NO_ERROR : Word := 16#0000;
      ERR_OCTET_WRONG_NUMBER_OF_CHAR : Word := 16#8110;
      ERR_OCTET_STRING_IS_EMPTY : Word := 16#8120;
      ERR_OCTET_EXCEEDS_MAX_IP_ADDRESS : Word := 16#8130;
      ERR_PORT_WRONG_NUMBER_OF_CHAR : Word := 16#8150;
      ERR_PORT_STRING_IS_EMPTY : Word := 16#8151;
      ERR_PORT_EXCEEDS_MAX_PORT : Word := 16#8152;
      MAX_IP_ADDRESS_OCTET_NUMBER : USInt := 255;
      MAX_PORT_NUMBER : UInt := 65535;
      EMPTY_STRING : Int := 0;
      MAX_CHAR_FOR_IP_OCTET_NUMBER : Int := 4;
      MAX_CHAR_FOR_PORT_NUMBER : Int := 5;
      INIT_VAL : USInt := 0;
      NUMBER_OF_IP_OCTETS : Int := 4;
      CHAR_DOT : Char := '.';
      CHAR_COLON : Char := ':';
      CONVERT_FORMAT_TO_INTEGER : Word := 16#0000;
      CONVERT_START_POSITION : UInt := 1;
   END_VAR
BEGIN
	REGION Initialization
	  #tempAddressString := #ipAddressString;
	  #tempIpAdressTaddr.REM_IP_ADDR[1] := #INIT_VAL;
	  #tempIpAdressTaddr.REM_IP_ADDR[2] := #INIT_VAL;
	  #tempIpAdressTaddr.REM_IP_ADDR[3] := #INIT_VAL;
	  #tempIpAdressTaddr.REM_IP_ADDR[4] := #INIT_VAL;
	  #tempIpAdressTaddr.REM_PORT_NR := #INIT_VAL;
	  #StringToTaddr := #tempIpAdressTaddr;
	END_REGION
	REGION Process Address String  
	  REGION Process octests 1-4
	    FOR #tempOctetIndex := 1 TO #NUMBER_OF_IP_OCTETS BY 1 DO
	      IF #tempOctetIndex < #NUMBER_OF_IP_OCTETS THEN
	        #tempCharPosition := FIND(IN1 := #tempAddressString, IN2 := #CHAR_DOT);
	      ELSE
	        #tempCharPosition := FIND(IN1 := #tempAddressString, IN2 := #CHAR_COLON);
	        #tempPortNumberIsSpecified := (#tempCharPosition > 0);
	        IF NOT #tempPortNumberIsSpecified THEN
	          #tempCharPosition := LEN(#tempAddressString) + 1;
	        END_IF;
	      END_IF;
	      REGION Octet conversion
	        IF #tempCharPosition > #MAX_CHAR_FOR_IP_OCTET_NUMBER THEN
	          #error := TRUE;
	          #status := #ERR_OCTET_WRONG_NUMBER_OF_CHAR OR INT_TO_WORD(#tempOctetIndex);
	          #StringToTaddr := #tempIpAdressTaddr;
	          RETURN;
	        END_IF;
	        #tempOctetString := LEFT(IN := #tempAddressString, L := #tempCharPosition - 1);
	        IF LEN(#tempOctetString) = #EMPTY_STRING THEN
	          #error := TRUE;
	          #status := #ERR_OCTET_STRING_IS_EMPTY OR INT_TO_WORD(#tempOctetIndex);
	          #StringToTaddr := #tempIpAdressTaddr;
	          RETURN;
	        END_IF;
	        STRG_VAL(IN     := #tempOctetString,
	                 FORMAT := #CONVERT_FORMAT_TO_INTEGER,
	                 P      := #CONVERT_START_POSITION,
	                 OUT    => #tempNumber);
	        IF #tempNumber > #MAX_IP_ADDRESS_OCTET_NUMBER THEN
	          #error := TRUE;
	          #status := #ERR_OCTET_EXCEEDS_MAX_IP_ADDRESS OR INT_TO_WORD(#tempOctetIndex);
	          #StringToTaddr := #tempIpAdressTaddr;
	          RETURN;
	        END_IF;
	        #tempIpAdressTaddr.REM_IP_ADDR[#tempOctetIndex] := UDINT_TO_USINT(#tempNumber);
	        #tempAddressString := DELETE(IN := #tempAddressString, P := 1, L := #tempCharPosition);
	      END_REGION Octet conversion
	    END_FOR;
	  END_REGION Process octests 1-4
	  REGION PORT number conversion
	    IF #tempPortNumberIsSpecified THEN
	      IF LEN(#tempAddressString) > #MAX_CHAR_FOR_PORT_NUMBER THEN
	        #error := TRUE;
	        #status := #ERR_PORT_WRONG_NUMBER_OF_CHAR;
	        #StringToTaddr := #tempIpAdressTaddr;
	        RETURN;
	      ELSIF LEN(#tempAddressString) = #EMPTY_STRING THEN
	        #error := TRUE;
	        #status := #ERR_PORT_STRING_IS_EMPTY;
	        #StringToTaddr := #tempIpAdressTaddr;
	        RETURN;
	      END_IF;
	      STRG_VAL(IN     := #tempAddressString,
	               FORMAT := #CONVERT_FORMAT_TO_INTEGER,
	               P      := #CONVERT_START_POSITION,
	               OUT    => #tempNumber);
	      IF #tempNumber > #MAX_PORT_NUMBER THEN
	        #error := TRUE;
	        #status := #ERR_PORT_EXCEEDS_MAX_PORT;
	        #StringToTaddr := #tempIpAdressTaddr;
	        RETURN;
	      END_IF;
	      #tempIpAdressTaddr.REM_PORT_NR := UDINT_TO_UINT(#tempNumber);
	    END_IF;
	  END_REGION PORT number conversion
	END_REGION
	REGION Outputs
	  #error := FALSE;
	  #status := #STATUS_FINISHED_NO_ERROR;
	  #StringToTaddr := #tempIpAdressTaddr;
	  ENO := TRUE;
	END_REGION
END_FUNCTION
题目十五输入:
{
    "title": "温度逻辑控制",
    "description": "编写一个函数块FB，实现一个温度控制逻辑。该程序应包含以下功能：
1. 通过模拟量输入模块读取温度传感器的值。
2. 将读取的温度值TemperatureSensorInput与设定的温度值SetTemperature进行比较。
3. 如果实际温度低于设定温度，则启动加热器HeaterOutput。
4. 如果实际温度高于设定温度，则关闭加热器HeaterOutput。
5. 如果加热器连续工作超过一定时间（为方便测试，采用5s），应触发过热保护，自动关闭加热器，必须再过一定时间（为方便测试，采用3s）才能解除过热保护。
6. 提供状态指示，显示当前温度、设定温度、加热器状态以及是否有过热保护触发。
7. 提供温度传感器故障判断，如果读取的温度值TemperatureSensorInput小于0或大于100，则认为传感器故障，此时应关闭加热器。",
    "type": "FUNCTION_BLOCK",
    "name": "TempCtrl",
    "input": [
        {
            "name": "TemperatureSensorInput",
            "type": "Real",
            "description": "温度传感器输入值，即实际温度"
        },
        {
            "name": "SetTemperature",
            "type": "Real",
            "description": "设定温度值"
        }
    ],
    "output": [
        {
            "name": "CurrentTemperature",
            "type": "Real",
            "description": "当前温度显示"
        },
        {
            "name": "SetTempDisplay",
            "type": "Real",
            "description": "设定温度显示"
        },
        {
            "name": "HeaterStatus",
            "type": "Bool",
            "description": "加热器状态显示"
        },
        {
            "name": "OverheatProtection",
            "type": "Bool",
            "description": "过热保护状态显示"
        }
    ],
    "in/out": [
        {
            "name": "HeaterOutput",
            "type": "Bool",
            "description": "加热器控制输出"
        }
    ]
}
题目十五输出:
FUNCTION_BLOCK "TempCtrl"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      TemperatureSensorInput : Real;   
      SetTemperature : Real;   
   END_VAR
   VAR_OUTPUT 
      CurrentTemperature : Real;   
      SetTempDisplay : Real;   
      HeaterStatus : Bool;   
      OverheatProtection : Bool;   
   END_VAR
   VAR_IN_OUT 
      HeaterOutput : Bool;   
   END_VAR
   VAR 
      HeaterState : Struct
         IsEnabled : Bool;
         OverheatProtectionTriggered : Bool;
      END_STRUCT;
      OverheatTimer  : TON_TIME;   
      SensorError : Bool;   
      CoolTimer  : TON_TIME;
      OverheatTimerOutput  : Bool;
      CoolTimerOutput  : Bool;
   END_VAR
BEGIN
	#CurrentTemperature := #TemperatureSensorInput;
	#SetTempDisplay := #SetTemperature;
	IF #TemperatureSensorInput < 0 OR #TemperatureSensorInput > 100 THEN
	    #SensorError := TRUE;
	ELSE
	    #SensorError := FALSE;
	END_IF;
	#OverheatTimer(IN := #HeaterOutput,
	               PT := T#5S,
	               Q => #OverheatTimerOutput);
	IF #HeaterState.IsEnabled AND #OverheatTimerOutput THEN
	    #HeaterState.OverheatProtectionTriggered := TRUE;
	    #HeaterState.IsEnabled := FALSE;
	    #HeaterOutput := FALSE;
	END_IF;
	#CoolTimer(IN := #HeaterState.OverheatProtectionTriggered,
	           PT := t#3S,
	           Q => #CoolTimerOutput);
	IF #CoolTimerOutput THEN
	    #HeaterState.OverheatProtectionTriggered := FALSE ;
	END_IF;
	IF NOT #SensorError THEN
	    IF #CurrentTemperature < #SetTemperature AND NOT #HeaterState.OverheatProtectionTriggered THEN
	        IF NOT #HeaterState.IsEnabled THEN
	            #HeaterState.IsEnabled := TRUE;
	            #HeaterOutput := TRUE;
	        END_IF;
	    ELSIF #CurrentTemperature > #SetTemperature THEN
	        IF #HeaterState.IsEnabled THEN
	            #HeaterState.IsEnabled := FALSE;
	            #HeaterOutput := FALSE;
	        END_IF;
	    END_IF;
	ELSE
	    #HeaterOutput := FALSE;
	    #HeaterState.IsEnabled := FALSE;
	END_IF;
	#HeaterStatus := #HeaterState.IsEnabled;
	#OverheatProtection := #HeaterState.OverheatProtectionTriggered;
END_FUNCTION_BLOCK
题目十六输入:
{
    "title": "计算一年中的第几天",
    "description": "在某些自动化系统中，可能需要根据当前日期计算出它是一年中的第几天。这可以用于追踪生产周期、维护计划或其他需要日期信息的场合。\n控制要求：\n系统需要接收日期输入，包括年、月、日。\n根据输入的日期，计算并输出它是一年中的第几天。\n考虑到不同年份的2月天数可能不同（平年28天，闰年29天），系统需要能够识别闰年并相应地计算。\n输出结果应该是一个整数，表示一年中的第几天。\n如果输入的日期不合法（如2月30日、4月31日等），系统应输出错误状态和错误代码。\n说明：\n1. 要求输入的年份Year在1000到3000之间（包括1000和3000），否则输出错误状态error=true和错误代码status=16#8001。如果输入的月份Month不合法，则输出错误状态error=true和错误代码status=16#8002。如果输入的日Day不合法，则输出错误状态error=true和错误代码status=16#8003。\n2. 计算的结果通过DayOfYear输出。",
    "type": "FUNCTION_BLOCK",
    "name": "FB_CalculateDayOfYear",
    "input": [
        {
            "name": "Year",
            "type": "Int",
            "description": "年份输入"
        },
        {
            "name": "Month",
            "type": "Int",
            "description": "月份输入"
        },
        {
            "name": "Day",
            "type": "Int",
            "description": "日输入"
        }
    ],
    "output": [
        {
            "name": "DayOfYear",
            "type": "Int",
            "description": "一年中的第几天输出"
        },
        {
            "name": "error",
            "type": "Bool",
            "description": "错误状态指示\nFALSE: 没有发生错误\nTRUE: 执行出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ]
}
题目十六输出:
FUNCTION_BLOCK "FB_CalculateDayOfYear"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      Year : Int;
      Month : Int;
      Day : Int;
   END_VAR
   VAR_OUTPUT 
      DayOfYear : Int;
      error : Bool;
      status : Word;
   END_VAR
   VAR 
      statDaysInMonth : Array[1..12] of Int;
      statLeapYear : Bool;
   END_VAR
   VAR_TEMP 
      tempDaysInMonth : Array[1..12] of Int;
      tempLeapYear : Bool;
      tempDayOfYear : Int;
   END_VAR
   VAR CONSTANT 
      STATUS_FINISHED_NO_ERROR : Word := 16#0000;
      ERR_YEAR_OUT_OF_RANGE : Word := 16#8001;
      ERR_MONTH_OUT_OF_RANGE : Word := 16#8002;
      ERR_DAY_OUT_OF_RANGE : Word := 16#8003;
      MIN_YEAR : Int := 1000;
      MAX_YEAR : Int := 3000;
      MIN_MONTH : Int := 1;
      MAX_MONTH : Int := 12;
      MIN_DAY : Int := 1;
      MAX_DAY : Int := 31;
      DAYS_IN_FEBRUARY : Int := 28;
      DAYS_IN_LEAP_FEBRUARY : Int := 29;
      DAYS_IN_MONTH : Array[1..12] of Int := [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
   END_VAR
BEGIN
	REGION Initialization
	  #tempDaysInMonth := #DAYS_IN_MONTH;
	  #tempLeapYear := FALSE;
	  #tempDayOfYear := 0;
	  #FB_CalculateDayOfYear := #tempDayOfYear;
	END_REGION
	REGION Validation of inputs
	    IF (#Year < #MIN_YEAR) OR (#Year > #MAX_YEAR) THEN
	        #error := TRUE;
	        #status := #ERR_YEAR_OUT_OF_RANGE;
	        RETURN;
	    END_IF;
	    IF (#Month < #MIN_MONTH) OR (#Month > #MAX_MONTH) THEN
	        #error := TRUE;
	        #status := #ERR_MONTH_OUT_OF_RANGE;
	        RETURN;
	    END_IF;
	    IF (#Day < #MIN_DAY) OR (#Day > #MAX_DAY) THEN
	        #error := TRUE;
	        #status := #ERR_DAY_OUT_OF_RANGE;
	        RETURN;
	    END_IF;
	END_REGION
	REGION Leap year calculation
	    IF (#Year MOD 4 = 0) AND ((#Year MOD 100 <> 0) OR (#Year MOD 400 = 0)) THEN
	        #tempLeapYear := TRUE;
	    END_IF;
	    IF #tempLeapYear THEN
	        #tempDaysInMonth[2] := #DAYS_IN_LEAP_FEBRUARY;
	    END_IF;
	END_REGION
	REGION Calculating the day of the year
	    FOR #tempDayOfYear := 1 TO #Month - 1 DO
	        #tempDayOfYear += #tempDaysInMonth[#tempDayOfYear];
	    END_FOR;
	    #tempDayOfYear += #Day;
	END_REGION
	REGION Outputs
	    #DayOfYear := #tempDayOfYear;
	    #error := FALSE;
	    #status := #STATUS_FINISHED_NO_ERROR;
	    ENO := TRUE;
	END_REGION
END_FUNCTION_BLOCK

题目十七输入:
{
    "title": "控制台指示灯顺序控制",
    "description": "某控制台装有3个指示灯，分别为绿色、红色和黄色。需要通过一个控制按钮来循环控制这些灯的状态。\n控制要求：\n使用一个输入参数controlButton表示控制按钮的状态，该按钮为脉冲信号，每次触发时产生一个从0到1的跳变。\n使用三个输出参数greenLight、redLight、yellowLight分别来控制对应的绿色、红色和黄色指示灯。\n控制按钮触发的顺序和对应指示灯的状态如下：\n第1次触发：只有绿灯greenLight亮。\n第2次触发：只有红灯redLight亮。\n第3次触发：只有黄灯yellowLight亮。\n第4次触发：3个灯都亮。\n第5次触发：3个灯都灭。\n第6次触发及以后：重复上述循环。",
    "type": "FUNCTION_BLOCK",
    "name": "FB_ColorLightControl",
    "input": [
        {
            "name": "controlButton",
            "type": "Bool",
            "description": "控制按钮开关，脉冲信号"
        }
    ],
    "output": [
        {
            "name": "greenLight",
            "type": "Bool",
            "description": "绿色指示灯"
        },
        {
            "name": "redLight",
            "type": "Bool",
            "description": "红色指示灯"
        },
        {
            "name": "yellowLight",
            "type": "Bool",
            "description": "黄色指示灯"
        }
    ]
}
题目十七输出:
FUNCTION_BLOCK "FB_ColorLightControl"
{ S7_Optimized_Access := 'TRUE' }
VAR_INPUT 
    controlButton : Bool;
END_VAR
VAR_OUTPUT 
    greenLight : Bool;
    redLight : Bool;
    yellowLight : Bool;
END_VAR
VAR 
    buttonPressed : Bool;
    trigger : Bool;
    lightState : Int;
END_VAR
BEGIN
    #trigger := #controlButton AND NOT #buttonPressed;
    #buttonPressed := #controlButton;
    IF #trigger THEN
        #lightState := #lightState + 1;
        IF #lightState > 5 THEN
            #lightState := 1;
        END_IF;
    END_IF;
    CASE #lightState OF
        1:
            #greenLight := TRUE;
            #redLight := FALSE;
            #yellowLight := FALSE;
        2:
            #greenLight := FALSE;
            #redLight := TRUE;
            #yellowLight := FALSE;
        3:
            #greenLight := FALSE;
            #redLight := FALSE;
            #yellowLight := TRUE;
        4:
            #greenLight := TRUE;
            #redLight := TRUE;
            #yellowLight := TRUE;
        5:
            #greenLight := FALSE;
            #redLight := FALSE;
            #yellowLight := FALSE;
    END_CASE;
END_FUNCTION_BLOCK


题目十八输入:
{
    "title": "16位二进制数分解为四个4位二进制数",
    "description": "在一些数据处理和通信应用中，需要将一个16位的二进制数分解成四个独立的4位二进制数。例如，在数据编码、解码或与外部系统的数据交换时，可能需要这种分解操作。\n控制要求：\n系统需要接收一个16位的二进制数InputWord作为输入。\n将输入的16位二进制数分解成四个4位的二进制数，分别对应输入数的最低位到最高位。\n输出这四个4位二进制数到独立的变量Byte0~Byte3中。\n同时对这4个变量Byte0~Byte3中非0的变量求取平均值，并输出到average。\n例如，InputWord=16#1203，则Byte0=3，Byte1=0，Byte2=2，Byte3=1，那么平均值average=(1+2+3)/3",
    "type": "FUNCTION_BLOCK",
    "name": "FB_SplitWordIntoBytes",
    "input": [
        {
            "name": "InputWord",
            "type": "Word",
            "description": "16位二进制数输入"
        }
    ],
    "output": [
        {
            "name": "Byte0",
            "type": "Byte",
            "description": "最低的4位二进制数输出"
        },
        {
            "name": "Byte1",
            "type": "Byte",
            "description": "次低的4位二进制数输出"
        },
        {
            "name": "Byte2",
            "type": "Byte",
            "description": "次高的4位二进制数输出"
        },
        {
            "name": "Byte3",
            "type": "Byte",
            "description": "最高的4位二进制数输出"
        },
        {
            "name": "average",
            "type": "Real",
            "description": "四个字节中非零字节的平均值"
        }
    ]
}
题目十八输出:
FUNCTION_BLOCK "FB_SplitWordIntoBytes"
{ S7_Optimized_Access := 'TRUE' }
   VAR_INPUT 
      InputWord : Word;
   END_VAR
   VAR_OUTPUT 
      Byte0 : Byte;
      Byte1 : Byte;
      Byte2 : Byte;
      Byte3 : Byte;
      average : Real;
   END_VAR
   VAR 
      tempSum : Real;
      tempCount : Int;
   END_VAR
BEGIN
    #Byte0 := Word_TO_Byte(#InputWord MOD 16);
    #Byte1 := Word_TO_Byte((#InputWord / 16) MOD 16);
    #Byte2 := Word_TO_Byte((#InputWord / 256) MOD 16);
    #Byte3 := Word_TO_Byte((#InputWord / 4096) MOD 16);
    #tempSum := 0.0;
    #tempCount := 0;
    IF #Byte0 > 0 THEN
        #tempSum := #tempSum + #Byte0;
        #tempCount := #tempCount + 1;
    END_IF;
    IF #Byte1 > 0 THEN
        #tempSum := #tempSum + #Byte1;
        #tempCount := #tempCount + 1;
    END_IF;
    IF #Byte2 > 0 THEN
        #tempSum := #tempSum + #Byte2;
        #tempCount := #tempCount + 1;
    END_IF;
    IF #Byte3 > 0 THEN
        #tempSum := #tempSum + #Byte3;
        #tempCount := #tempCount + 1;
    END_IF;
    IF #tempCount > 0 THEN
        #average := #tempSum / #tempCount;
    ELSE
        #average := 0.0;
    END_IF;
    ENO := TRUE;
END_FUNCTION_BLOCK

题目十九输入:
{
    "title": "PLC数据库数据存储与管理系统",
    "description": "在一些自动化应用中，PLC需要收集和存储大量的数据，例如传感器读数、生产计数或其他过程变量。这些数据通常存储在PLC的内部数据库或外部数据库系统中。\n控制要求：\n系统需要接收一组数据dataInput，以字节数组构建，这组数据的第一个字节dataInput[0]表示要存入的数据字节长度。\n数据的存储操作由输入storeTrigger触发。\n数据需要依次存入数据库，每组数据长度可能不同。\n当数据库剩余空间不足以存入新的一组数据时，系统应触发报错error。\n系统应提供一个复位功能，通过输入resetTrigger来清空数据库，并重置error。\n系统应能够输出数据库的当前使用情况和剩余空间。\n说明：\n1. 当存储信号storeTrigger触发时，首先检查数据输入长度信息（即数组的首字节dataInput[0]）是否非法，如果小于等于0或大于5，则输出错误状态error=true和错误代码status=16#8001。如果数据库剩余空间不足以存入新数据，则输出错误状态error=true和错误代码status=16#8002。如果没有这些错误，则根据长度信息，把从输入数组的第二字节开始的数据取出，并存入数据库。存入时不能覆盖数据库原有的数据，从原有数据之后依次存入。\n2. 当复位信号resetTrigger触发时，清空数据库中所有数据，并复位错误状态error=0和status=0。\n3. 数据库已使用空间和剩余空间分别通过usedSpace和remainingSpace输出。",
    "type": "FUNCTION_BLOCK",
    "name": "FB_DatabaseManager",
    "input": [
        {
            "name": "dataInput",
            "type": "Array[0..5] of Byte",
            "description": "数据输入，字节数组"
        },
        {
            "name": "storeTrigger",
            "type": "Bool",
            "description": "存储触发信号"
        },
        {
            "name": "resetTrigger",
            "type": "Bool",
            "description": "复位触发信号"
        }
    ],
    "output": [
        {
            "name": "usedSpace",
            "type": "Int",
            "description": "数据库已使用空间"
        },
        {
            "name": "remainingSpace",
            "type": "Int",
            "description": "数据库剩余空间"
        },
        {
            "name": "error",
            "type": "Bool",
            "description": "错误状态指示\nFALSE:没有发生错误\nTRUE:执行出错"
        },
        {
            "name": "status",
            "type": "Word",
            "description": "状态代码"
        }
    ],
    "in/out": [
        {
            "name": "dataBase",
            "type": "Array[1..20] of Byte",
            "description": "数据库，字节数组"
        }
    ]
}
题目十九输出:
FUNCTION_BLOCK "FB_DatabaseManager"
{ S7_Optimized_Access := 'TRUE' }
VAR_INPUT 
    dataInput : Array[0..5] of Byte;
    storeTrigger : Bool;
    resetTrigger : Bool;
END_VAR
VAR_OUTPUT 
    usedSpace : Int;
    remainingSpace : Int;
    error : Bool;
    status : Word;
END_VAR
VAR_IN_OUT 
    "dataBase" : Array[*] of Byte;   
END_VAR
VAR 
    #currentIndex : Int;
    #dataLength : Int;
    #i : Int;
END_VAR
VAR CONSTANT 
    MAX_DB_SIZE : Int := 20;
    ERR_INVALID_LENGTH : Word := 16#8001;
    ERR_INSUFFICIENT_SPACE : Word := 16#8002;
    STATUS_NO_ERROR : Word := 16#0000;
END_VAR
BEGIN
    #error := FALSE;
    #status := #STATUS_NO_ERROR;
    IF #resetTrigger THEN
        FOR #currentIndex := 1 TO #MAX_DB_SIZE DO
            #dataBase[#currentIndex] := 0;
        END_FOR;
        #usedSpace := 0;
        #remainingSpace := #MAX_DB_SIZE;
        #error := FALSE;
        #status := #STATUS_NO_ERROR;
        RETURN;
    END_IF;
    #usedSpace := 0;
    FOR #currentIndex := 1 TO #MAX_DB_SIZE DO
        IF #dataBase[#currentIndex] <> 0 THEN
            #usedSpace := #usedSpace + 1;
        ELSE
            EXIT;
        END_IF;
    END_FOR;
    #remainingSpace := #MAX_DB_SIZE - #usedSpace;
    IF #storeTrigger THEN
        #dataLength := #dataInput[0];
        IF #dataLength <= 0 OR #dataLength > 5 THEN
            #error := TRUE;
            #status := #ERR_INVALID_LENGTH;
            RETURN;
        END_IF;
        IF #remainingSpace < #dataLength THEN
            #error := TRUE;
            #status := #ERR_INSUFFICIENT_SPACE;
            RETURN;
        END_IF;
        FOR #i := 1 TO #dataLength DO
            #dataBase[#usedSpace + #i] := #dataInput[#i];
        END_FOR;
        #usedSpace := #usedSpace + #dataLength;
        #remainingSpace := #MAX_DB_SIZE - #usedSpace;
        #error := FALSE;
        #status := #STATUS_NO_ERROR;
    END_IF;
    #usedSpace := #usedSpace;
    #remainingSpace := #remainingSpace;
END_FUNCTION_BLOCK

题目二十输入:
{
    "title": "浮点数区间线性化转换",
    "description": "在一些自动化控制系统中，可能需要将一个物理量（如温度、压力等）的测量值转换为另一个线性化或标准化的值，以便于控制算法的处理或显示。例如，一个传感器测量的物理量可能在特定的非线性区间内变化，但控制系统需要一个线性化的值来进行计算。\n控制要求：\n系统需要接收一个浮点数作为输入，表示原始测量值。\n根据输入值的大小，将其转换到不同的线性区间，输出转换后的线性化值。\n当输入值在1200到3600之间，则转换到150到240之间。\n当输入值在3600到4800之间，则转换到240到560之间。\n当输入值在4800到7000之间，则转换到560到720之间。\n如果输入值小于1200或大于7000，则转换后的值应为1200或7000对应的线性化值，并输出错误状态error=1，status=16#8001。",
    "type": "FUNCTION_BLOCK",
    "name": "FB_LinearizeValue",
    "input": [
        {
            "name": "InputValue",
            "type": "Real",
            "description": "浮点数输入，原始测量值"
        }
    ],
    "output": [
        {
            "name": "LinearizedValue",
            "type": "Real",
            "description": "转换后的线性化值"
        },
        {
            "name": "Error",
            "type": "Bool",
            "description": "错误状态指示\nFALSE: 没有发生错误\nTRUE: 执行出错"
        },
        {
            "name": "Status",
            "type": "Word",
            "description": "状态代码"
        }
    ]
}
题目二十输出:
FUNCTION_BLOCK "FB_LinearizeValue"
{ S7_Optimized_Access := 'TRUE' }
VAR_INPUT 
    InputValue : Real;
END_VAR
VAR_OUTPUT 
    LinearizedValue : Real;
    Error : Bool;
    Status : Word;
END_VAR
VAR CONSTANT 
    MIN_INPUT1 : Real := 1200.0;
    MAX_INPUT1 : Real := 3600.0;
    MIN_OUTPUT1 : Real := 150.0;
    MAX_OUTPUT1 : Real := 240.0;
    MIN_INPUT2 : Real := 3600.0;
    MAX_INPUT2 : Real := 4800.0;
    MIN_OUTPUT2 : Real := 240.0;
    MAX_OUTPUT2 : Real := 560.0;
    MIN_INPUT3 : Real := 4800.0;
    MAX_INPUT3 : Real := 7000.0;
    MIN_OUTPUT3 : Real := 560.0;
    MAX_OUTPUT3 : Real := 720.0;
    ERR_OUT_OF_RANGE : Word := 16#8001;
END_VAR
BEGIN
    #Error := FALSE;
    #Status := 16#0000;
    IF #InputValue < #MIN_INPUT1 THEN
        #LinearizedValue := #MIN_OUTPUT1;
        #Error := TRUE;
        #Status := #ERR_OUT_OF_RANGE;
    ELSIF #InputValue > #MAX_INPUT3 THEN
        #LinearizedValue := #MAX_OUTPUT3;
        #Error := TRUE;
        #Status := #ERR_OUT_OF_RANGE;
    ELSIF #InputValue >= #MIN_INPUT1 AND #InputValue <= #MAX_INPUT1 THEN
        #LinearizedValue := #MIN_OUTPUT1 + ((#InputValue - #MIN_INPUT1) * (#MAX_OUTPUT1 - #MIN_OUTPUT1) / (#MAX_INPUT1 - #MIN_INPUT1));
    ELSIF #InputValue >= #MIN_INPUT2 AND #InputValue <= #MAX_INPUT2 THEN
        #LinearizedValue := #MIN_OUTPUT2 + ((#InputValue - #MIN_INPUT2) * (#MAX_OUTPUT2 - #MIN_OUTPUT2) / (#MAX_INPUT2 - #MIN_INPUT2));
    ELSIF #InputValue >= #MIN_INPUT3 AND #InputValue <= #MAX_INPUT3 THEN
        #LinearizedValue := #MIN_OUTPUT3 + ((#InputValue - #MIN_INPUT3) * (#MAX_OUTPUT3 - #MIN_OUTPUT3) / (#MAX_INPUT3 - #MIN_INPUT3));
    END_IF;
END_FUNCTION_BLOCK

题目二十一输入:
{
    "title": "自动化生产线控制",
    "description": "一个简单的自动化生产线由三个工作站组成：工作站A、工作站B和工作站C。产品需要经过这三个站的依次加工后才算全部完成。生产线有一个电机，负责将产品从一个工作站移动到下一个工作站，生成线的顺序是从工作站A到工作站B，再到工作站C。每个工作站都有一个传感器（用于检测产品是否到达）以及一个按钮（用于触发本站加工完成信号）。\n控制要求：\n1. 模式切换：转换开关（Mode）用于切换生产线的手动和自动模式。\n2. 手动模式：在手动模式下，电机正转按钮（ForwardButton）控制电机正转，电机反转按钮（ReverseButton）控制电机反转，正反转操作需要互锁，不能同时进行。\n3. 自动模式：\n   - 产品到达工作站A，SensorA检测到产品，操作员通过ButtonA触发加工完成信号后，电机启动正转，将产品移动到工作站B。\n   - 产品到达工作站B，SensorB检测到产品，电机停止，操作员通过ButtonB触发加工完成信号后，电机启动正转，将产品移动到工作站C。\n   - 产品到达工作站C，SensorC检测到产品，电机停止，操作员通过ButtonC触发加工完成信号后，加工完成指示灯（CompletionLight）亮起，指示产品加工完成。当产品被取走，也就是SensorC检测不到产品了，加工完成指示灯（CompletionLight）熄灭。",
    "type": "FUNCTION_BLOCK",
    "name": "FB_ProductionLineControl",
    "input": [
        {
            "name": "Mode",
            "type": "Bool",
            "description": "用于切换生产线的手动和自动模式，0=手动模式，1=自动模式"
        },
        {
            "name": "ForwardButton",
            "type": "Bool",
            "description": "正转按钮"
        },
        {
            "name": "ReverseButton",
            "type": "Bool",
            "description": "反转按钮"
        },
        {
            "name": "SensorA",
            "type": "Bool",
            "description": "传感器A"
        },
        {
            "name": "SensorB",
            "type": "Bool",
            "description": "传感器B"
        },
        {
            "name": "SensorC",
            "type": "Bool",
            "description": "传感器C"
        },
        {
            "name": "ButtonA",
            "type": "Bool",
            "description": "按钮A"
        },
        {
            "name": "ButtonB",
            "type": "Bool",
            "description": "按钮B"
        },
        {
            "name": "ButtonC",
            "type": "Bool",
            "description": "按钮C"
        }
    ],
    "output": [
        {
            "name": "MotorForward",
            "type": "Bool",
            "description": "电机正转输出"
        },
        {
            "name": "MotorReverse",
            "type": "Bool",
            "description": "电机反转输出"
        },
        {
            "name": "CompletionLight",
            "type": "Bool",
            "description": "产品加工完成指示灯"
        }
    ]
}
题目二十一输出:
FUNCTION_BLOCK "FB_ProductionLineControl"
{ S7_Optimized_Access := 'TRUE' }
VAR_INPUT
    #Mode : Bool;
    #ForwardButton : Bool;
    #ReverseButton : Bool;
    #SensorA : Bool;
    #SensorB : Bool;
    #SensorC : Bool;
    #ButtonA : Bool;
    #ButtonB : Bool;
    #ButtonC : Bool;
END_VAR
VAR_OUTPUT
    #MotorForward : Bool;
    #MotorReverse : Bool;
    #CompletionLight : Bool;
END_VAR
VAR
    #State : Int;
END_VAR
BEGIN
    IF #Mode = FALSE THEN
        #MotorForward := #ForwardButton AND NOT #ReverseButton;
        #MotorReverse := #ReverseButton AND NOT #ForwardButton;
    ELSE
        CASE #State OF
            0:
                #MotorForward := FALSE;
                #MotorReverse := FALSE;
                IF #SensorA THEN
                    #State := 1;
                END_IF;
            1:
                IF #ButtonA THEN
                    #MotorForward := TRUE;
                    #MotorReverse := FALSE;
                    #State := 2;
                END_IF;
            2:
                IF #SensorB THEN
                    #MotorForward := FALSE;
                    #MotorReverse := FALSE;
                    #State := 3;
                END_IF;
            3:
                IF #ButtonB THEN
                    #MotorForward := TRUE;
                    #MotorReverse := FALSE;
                    #State := 4;
                END_IF;
            4:
                IF #SensorC THEN
                    #MotorForward := FALSE;
                    #MotorReverse := FALSE;
                    #State := 5;
                END_IF;
            5:
                IF #ButtonC THEN
                    #CompletionLight := TRUE;
                    #State := 6;
                END_IF;
            6:
                IF NOT #SensorC THEN
                    #CompletionLight := FALSE;
                    #State := 0;
                END_IF;
        END_CASE;
    END_IF;
END_FUNCTION_BLOCK

以上就是全部样例.

注意:
```
不要把数组变量定义在VAR CONSTANT中
for循环若需要变量i请提前定义
除了在变量定义的地方，其他地方引用变量时都需要在变量名前加上`#`符号。
只需要输出代码本身, 不要输出```scl\n```这种形式
```


请输出本次输入题目的答案

输入:
"""

def generate_response(full_prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "你是一名SCL编程助手。你的职责是帮助用户理解并完成SCL语言的编程任务, 为了完成编程任务。用户会提供编程问题，你需要提供清晰、正确且格式良好的SCL代码作为解决方案, 为了此目标, 你会为编程任务准备一些测试并对你生成的代码进行测试,注意不要输出任何测试相关的信息, 只需要输出最终结果, 为用户提供代码时只需要输出代码本身, 不要输出```scl\n```这种形式的代码框。"},
            {"role": "user", "content": full_prompt}
        ],
        top_p=0.7,
        temperature=0.3,
        max_tokens=4096
    )
    return response.choices[0].message.content


@app.route('/', methods=['POST'])
def generate_code():
    data = request.get_json()
    input = json.dumps(data, ensure_ascii=False)
    # 将固定提示词和输入数据结合在一起
    full_prompt = prompt + input + """

    输出:
    """
    result = generate_response(full_prompt, model)
    response = {
        "name": data.get("name"),
        "code": result
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)