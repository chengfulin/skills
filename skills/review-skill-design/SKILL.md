---
name: review-skill-design
description: 檢核指定的 skills 與 agents 是否過度設計：是否造成 context 浪費或不必要的 tool_use 輪數，以及 opus 等級的模型是否足以理解執行並取得預期結果。只提供建議供 review，不修改檔案。當使用者要「檢核／審查某些 skill 或 agent 的設計」、「看這個 skill 有沒有過度設計」、「評估 skill 對 opus 夠不夠清楚」時使用。
argument-hint: <要檢核的 skill／agent 名稱或路徑，以空白分隔>
model: opus
---

幫我分析檢核以下指定的 skills 與 agents 是否有過度設計，造成 context 浪費或者不必要的 tool_use 輪數，以及對於 model opus 是否足夠理解執行取得預期結果。
先不要修改，僅先提供建議讓我 review。

要檢核的 skills & agents: $ARGUMENTS
