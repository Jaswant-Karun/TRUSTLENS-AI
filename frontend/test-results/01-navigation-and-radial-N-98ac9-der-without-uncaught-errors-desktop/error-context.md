# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 01-navigation-and-radial.spec.ts >> Navigation, Radial Wheel & All Routes >> all navigation routes render without uncaught errors
- Location: e2e\01-navigation-and-radial.spec.ts:52:3

# Error details

```
Test timeout of 45000ms exceeded.
```

# Page snapshot

```yaml
- generic [ref=f21e3]:
  - banner [ref=f21e4]:
    - generic [ref=f21e5]:
      - generic [ref=f21e6]:
        - button "Open primary radial navigation" [ref=f21e8] [cursor=pointer]
        - generic [ref=f21e12]: NAV WHEEL
      - link "TRUSTLENS AI" [ref=f21e13] [cursor=pointer]:
        - /url: /
  - main [ref=f21e25]:
    - generic [ref=f21e26]:
      - generic [ref=f21e27]:
        - navigation "Breadcrumb" [ref=f21e28]:
          - link "Home" [ref=f21e29] [cursor=pointer]:
            - /url: /
          - generic [ref=f21e35]: Records
          - generic [ref=f21e38]: Analysis History
        - heading "Analysis History & Incident Audit Trail" [level=1] [ref=f21e39]
      - navigation "Quick workflow navigation" [ref=f21e40]:
        - link "Messages" [ref=f21e41] [cursor=pointer]:
          - /url: /analyze/text
        - link "URLs" [ref=f21e42] [cursor=pointer]:
          - /url: /analyze/url
        - link "OCR" [ref=f21e43] [cursor=pointer]:
          - /url: /analyze/image
        - link "History" [ref=f21e44] [cursor=pointer]:
          - /url: /history
        - link "Investigations" [ref=f21e45] [cursor=pointer]:
          - /url: /investigations
        - link "Reports" [ref=f21e46] [cursor=pointer]:
          - /url: /reports
    - generic [ref=f21e47]:
      - generic [ref=f21e49]:
        - generic [ref=f21e50]:
          - heading "Analysis History" [level=1] [ref=f21e51]
          - generic [ref=f21e52]: 0 Stored Records
        - paragraph [ref=f21e53]: Persistent MongoDB record of your submitted message, URL, and screenshot analyses.
      - generic [ref=f21e54]:
        - textbox "Search by analysis ID, type, or threat level..." [ref=f21e59]
        - generic [ref=f21e60]:
          - combobox [ref=f21e61]:
            - option "All Threat Levels" [selected]
            - option "Critical Risk"
            - option "High Risk"
            - option "Medium Risk"
            - option "Clean / Safe"
          - combobox [ref=f21e62]:
            - option "All Vectors / Channels" [selected]
            - option "SMS"
            - option "WhatsApp"
            - option "Email"
            - option "URL"
            - option "Screenshot (OCR)"
          - combobox "Sort history" [ref=f21e63]:
            - option "Newest First" [selected]
            - option "Oldest First"
            - option "Highest Risk"
            - option "Lowest Risk"
```