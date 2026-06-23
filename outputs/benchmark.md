# Bảng so sánh Flat RAG vs GraphRAG (20 câu benchmark)

- **Flat RAG**: correct=14/20, hallucinated=2
- **GraphRAG**: correct=6/20, hallucinated=1

| # | Loại | Câu hỏi | Flat | Graph |
|---|------|---------|------|-------|
| 1 | single | What was Tesla's share of the US EV market in Q1 2024? | 🟡 | 🟡 |
| 2 | single | What was the EV share of total new-vehicle sales in the US i… | ✅ | ✅ |
| 3 | single | How many new electric vehicles did Americans buy in Q1 2024? | ❌ | ✅ |
| 4 | single | What was the average transaction price of a new EV in the US… | ✅ | ✅ |
| 5 | single | What happened to Chevy Bolt sales in Q1 2024 and why? | ✅ | ❌ |
| 6 | single | What EV tax credit does the Inflation Reduction Act offer? | ✅ | ✅ |
| 7 | single | What was the electric share of new-vehicle sales in the US i… | ❌ | ✅ |
| 8 | single | What full-year 2024 EV market share does Cox Automotive fore… | 🟡 | ✅ |
| 9 | multi-hop | Which automakers grew EV sales more than 50% year over year … | ✅ | 🟡 |
| 10 | multi-hop | How did Tesla's average transaction price compare with the o… | ✅ | 🟡 |
| 11 | multi-hop | How is the $7,500 IRA credit related to EV leasing trends? | ✅ | 🟡 |
| 12 | multi-hop | Which luxury automakers grew EV sales in Q1 2024 and by how … | ✅ | 🟡 |
| 13 | multi-hop | How did states with ZEV regulations differ from states witho… | ✅ | 🟡 |
| 14 | multi-hop | How did Tesla's US EV market share trend from Q1 2023 to Q1 … | ✅ | 🟡 |
| 15 | multi-hop | How did Ford's EV sales perform versus Tesla in Q1 2024? | 🟡 | 🟡 |
| 16 | multi-hop | Which model drove Cadillac's EV growth and how large was it? | ✅ | 🟡 |
| 17 | single | Who is the market leader in US EVs and what is the trend in … | 🟡 | 🟡 |
| 18 | multi-hop | What factors does Cox Automotive cite as driving EV sales hi… | ✅ | 🟡 |
| 19 | single | What share of EVs were leased in Q1 2024 compared with a yea… | ✅ | 🟡 |
| 20 | multi-hop | Compare the sales trends of luxury EVs versus the affordable… | ✅ | 🟡 |

## Chi tiết câu trả lời

**Q1 (single). What was Tesla's share of the US EV market in Q1 2024?**  
- *Đáp án đúng:* 51.3%, down from 61.7% a year earlier  
- Flat 🟡: Tesla's share of the US EV market in Q1 2024 was 51.3%.  
- Graph 🟡: Tesla's share of the US EV market in Q1 2024 was 51.3%.  

**Q2 (single). What was the EV share of total new-vehicle sales in the US in Q1 2024?**  
- *Đáp án đúng:* 7.3%  
- Flat ✅: The EV share of total new-vehicle sales in the US in Q1 2024 was 7.3%.  
- Graph ✅: The EV share of total new-vehicle sales in the US in Q1 2024 was 7.3%.  

**Q3 (single). How many new electric vehicles did Americans buy in Q1 2024?**  
- *Đáp án đúng:* 268,909 (per Kelley Blue Book)  
- Flat ❌: Not enough information.  
- Graph ✅: Americans bought 268,909 new electric vehicles in Q1 2024.  

**Q4 (single). What was the average transaction price of a new EV in the US in Q1 2024?**  
- *Đáp án đúng:* $55,167, down about 9% year over year  
- Flat ✅: The average transaction price of a new EV in the US in Q1 2024 was $55,167.  
- Graph ✅: The average transaction price of a new EV in the US in Q1 2024 was $55,167.  

**Q5 (single). What happened to Chevy Bolt sales in Q1 2024 and why?**  
- *Đáp án đúng:* Fell 64.3% to 7,040 units because production was halted; a new version is expected in 2025  
- Flat ✅: Chevy Bolt sales fell 64.3% year over year in Q1 2024, hitting just 7,040, as production was temporarily halted.  
- Graph ❌: Not enough information  

**Q6 (single). What EV tax credit does the Inflation Reduction Act offer?**  
- *Đáp án đúng:* $7,500 per EV  
- Flat ✅: The Inflation Reduction Act offers new tax credits of up to $7,500 for new electric vehicle (EV) purchases.  
- Graph ✅: The Inflation Reduction Act offers a $7,500 tax credit for EVs.  

**Q7 (single). What was the electric share of new-vehicle sales in the US in 2020?**  
- *Đáp án đúng:* About 2.4% (up from ~2% in 2019)  
- Flat ❌: Not enough information.  
- Graph ✅: The electric share of new-vehicle sales in the US in 2020 was approximately 2.4%.  

**Q8 (single). What full-year 2024 EV market share does Cox Automotive forecast?**  
- *Đáp án đúng:* About 10% by the end of 2024  
- Flat 🟡: Cox Automotive forecasts that EV sales in the U.S. will surpass the 10% market share mark for the first time in 2024.  
- Graph ✅: Cox Automotive forecasts the US EV market share to reach roughly 10% by the end of 2024.  

**Q9 (multi-hop). Which automakers grew EV sales more than 50% year over year in Q1 2024, and how did Tesla's sales change in the same period?**  
- *Đáp án đúng:* BMW, Cadillac, Ford, Hyundai, Kia, Lexus, Mercedes, Rivian and Vinfast grew >50%; Tesla fell about 13.3%  
- Flat ✅: In Q1 2024, the automakers that grew EV sales more than 50% year over year were BMW, Cadillac, Ford, Hyundai, Kia, Lexus, Mercedes, Rivian, and Vinfast. Tesla's sales in the U.S. were down 13.3% year …  
- Graph 🟡: In Q1 2024, Ford achieved an 86.1% year-over-year increase in EV sales, and Cadillac recorded a 499.2% year-over-year increase. Tesla's sales were down 13.3% year over year in the same period.  

**Q10 (multi-hop). How did Tesla's average transaction price compare with the overall new-EV average in Q1 2024?**  
- *Đáp án đúng:* Tesla's was $52,315, lower than the overall average of $55,167  
- Flat ✅: Tesla's average transaction price in Q1 2024 was $52,315, which was lower than the overall new-EV average of $55,167.  
- Graph 🟡: Tesla's average transaction price was lower than the overall new-EV average in Q1 2024. Tesla's average transaction price was USD 50,051 by December 2023, while the US EV market's average transaction …  

**Q11 (multi-hop). How is the $7,500 IRA credit related to EV leasing trends?**  
- *Đáp án đúng:* Leasing lets buyers qualify for the full $7,500, so leasing more than doubled to about 27%  
- Flat ✅: The $7,500 IRA credit is related to EV leasing trends in that many buyers can qualify for the full incentive through leasing. This has contributed to an increase in leasing, with roughly 27% of all EV…  
- Graph 🟡: Not enough information  

**Q12 (multi-hop). Which luxury automakers grew EV sales in Q1 2024 and by how much?**  
- *Đáp án đúng:* Cadillac +499.2% (Lyriq), Mercedes +66.9%, BMW +62.6%, Audi +28.8%  
- Flat ✅: In Q1 2024, the luxury automakers that grew EV sales were:  - Cadillac, with a 499.2% year-over-year increase. - Mercedes, with a 66.9% increase. - BMW, with a 62.6% increase. - Audi, with a 28.8% inc…  
- Graph 🟡: Cadillac recorded a 499.2% year-over-year increase in EV sales in Q1 2024.  

**Q13 (multi-hop). How did states with ZEV regulations differ from states without them in EV market share?**  
- *Đáp án đúng:* ZEV states had ~5% EV share vs ~1.3% in non-ZEV states  
- Flat ✅: States with ZEV regulations had a combined new electric vehicle share of 5%, while states without such regulations had a 1.3% average electric vehicle share.  
- Graph 🟡: States with ZEV regulations had a combined new electric vehicle share of 5% in 2020. Not enough information is provided about states without ZEV regulations to compare their EV market share.  

**Q14 (multi-hop). How did Tesla's US EV market share trend from Q1 2023 to Q1 2024?**  
- *Đáp án đúng:* Declined from 61.7% (Q1 2023) to 51.3% (Q1 2024)  
- Flat ✅: Tesla's US EV market share decreased from 61.7% in Q1 2023 to 51.3% in Q1 2024.  
- Graph 🟡: Tesla's US EV market share decreased from 55% in 2023 to 51.3% in Q1 2024.  

**Q15 (multi-hop). How did Ford's EV sales perform versus Tesla in Q1 2024?**  
- *Đáp án đúng:* Ford rose 86.1% YoY (second-highest EV volume), while Tesla fell about 13.3%  
- Flat 🟡: Ford's EV sales in Q1 2024 achieved an 86.1% year-over-year increase, with the second-highest EV sales volume behind Tesla. However, Ford's EV sales represented just 5% of Tesla's sales in the same pe…  
- Graph 🟡: Not enough information.  

**Q16 (multi-hop). Which model drove Cadillac's EV growth and how large was it?**  
- *Đáp án đúng:* The Lyriq; Cadillac grew 499.2% year over year  
- Flat ✅: Cadillac's EV growth was driven by robust sales of its Lyriq model, achieving a 499.2% year-over-year increase in electric vehicle sales.  
- Graph 🟡: Not enough information  

**Q17 (single). Who is the market leader in US EVs and what is the trend in its share?**  
- *Đáp án đúng:* Tesla leads but its share is declining (51.3%, down from 61.7%)  
- Flat 🟡: Tesla is the market leader in US EVs, holding approximately 50.9% of the EV market as of the last quarter of 2023. The trend in its share is not explicitly detailed in the provided context.  
- Graph 🟡: Tesla is the market leader in US EVs, holding a market share of approximately 50.9% in the last quarter of 2023.  

**Q18 (multi-hop). What factors does Cox Automotive cite as driving EV sales higher in 2024 (the 'Year of More')?**  
- *Đáp án đúng:* More new products, more incentives, more inventory, more leasing and more charging infrastructure  
- Flat ✅: Cox Automotive cites more new products, more incentives, more inventory, more leasing, and more infrastructure as factors driving EV sales higher in 2024, referred to as the 'Year of More'.  
- Graph 🟡: Not enough information  

**Q19 (single). What share of EVs were leased in Q1 2024 compared with a year earlier?**  
- *Đáp án đúng:* About 27%, more than double the prior year  
- Flat ✅: In Q1 2024, roughly 27% of all EVs were leased, more than double from the year before.  
- Graph 🟡: 27% of EVs were leased in Q1 2024. Not enough information is provided to compare this with a year earlier.  

**Q20 (multi-hop). Compare the sales trends of luxury EVs versus the affordable Chevy Bolt in Q1 2024.**  
- *Đáp án đúng:* Luxury surged (Cadillac +499.2%, Mercedes +66.9%, BMW +62.6%) while the Chevy Bolt fell 64.3% due to halted production  
- Flat ✅: In Q1 2024, luxury EVs showed strong sales growth, with Cadillac achieving a 499.2% year-over-year increase due to robust sales of its Lyriq model. Mercedes and BMW also saw significant increases in E…  
- Graph 🟡: Not enough information  

## ⭐ Trường hợp Flat RAG ảo giác/sai nhưng GraphRAG trả lời đúng

- **Q3. How many new electric vehicles did Americans buy in Q1 2024?**
  - Flat (hallucinated): _Not enough information._
  - Graph (correct): _Americans bought 268,909 new electric vehicles in Q1 2024._
  - Node đồ thị dùng: $388 billion (2022), 0% of models (2022), 1 million (by Q3 2023), 1.2 million (2023), 1.3 billion (by 2040), 10% (2023 relative to 2022)
- **Q7. What was the electric share of new-vehicle sales in the US in 2020?**
  - Flat (hallucinated): _Not enough information._
  - Graph (correct): _The electric share of new-vehicle sales in the US in 2020 was approximately 2.4%._
  - Node đồ thị dùng: 1% (2023), 1.2 million (2023), 13.3 million units (16.2% of global passenger vehicle sales), 14 million (2023), 15% (2019), 15% (2023)
- **Q8. What full-year 2024 EV market share does Cox Automotive forecast?**
  - Flat (partial): _Cox Automotive forecasts that EV sales in the U.S. will surpass the 10% market share mark for the first time in 2024._
  - Graph (correct): _Cox Automotive forecasts the US EV market share to reach roughly 10% by the end of 2024._
  - Node đồ thị dùng: 1 million (early 2023), 1.47 million units, 1.9% in 2019 to 2.3% in 2020, 10% (coming year), 10% (end of 2024, up from 7.3% in Q1), 12% (2024)