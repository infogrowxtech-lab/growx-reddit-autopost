# Growx Tech IT – Reddit Auto Poster

Ye system GitHub ke servers pe free chalta hai, isliye PC on rakhne ki zaroorat nahi hai.

## Kaise chalta hai
- Roz 3 baar (lagbhag 10:15, 14:45, 20:15 IST) check karta hai aur din me **1–3 posts** daalta hai. Kitne post jayenge, ye har din random hota hai.
- Pehle **14 din** sirf 1 post/day jayega, taaki naya account safe rahe.
- Posts `queue/` folder se number ke order me jaate hain (001, 002, ...).

## Proofreading
- `queue/` me koi bhi file kholo aur ✏️ se edit karo.
- Koi post nahi chahiye to us file ko **delete** kar do.
- Jo post ho chuke hain wo `posted/` me chale jaate hain, saath me unka Reddit link bhi hota hai.
- Jo fail hue (subreddit rule ki wajah se) wo `failed/` me jaate hain, error ke saath.

## Rokna / chalu karna
- **Pause:** repo me `PAUSE` naam ki ek khaali file bana do. Use delete karoge to posting phir chalu ho jayegi.
- **Test post abhi:** Actions → "Reddit auto post" → Run workflow → force ✅

## Naya post kaise add karein
`queue/` me nayi file banao, jaise `031.md`:
```
---
subreddit: smallbusiness
title: Aapka title
---

Post ka text...
```
