我想做一個基於LLM的虛擬AI場景的互動，請參考以下方式

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: XXX' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'


並且每次輸出時，LLM需要先輸出前景圖片image(image/emoji表情符號)與背景圖(image/background用來表達場域)
我想以一個透天建築為主，請你構想4個場景(房間中的電腦(控制電腦或檢索網路)，房間中的床(代表休息)，工作室(正在使用MCP)、繪圖室(正在規劃))

務必使用我提供的mcp_pipe與該系統對接。

初期場景，我希望模擬MCP的狀況即可，暫時不會有MCP的執行結果，我需要再初期就有完整的前端介面，後端將在後續實作(只需要先實作基礎的LLM即可)。


