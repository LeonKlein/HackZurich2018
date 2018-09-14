using HtmlAgilityPack;
using Newtonsoft.Json;
using Scrapper.Models;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace Scrapper.Services
{
    public class RecipeScrapper
    {
        public async Task Run()
        {
            string urlFormat = "https://www.allrecipes.com/recipe/{0}";
            string startId = (string)ConfigurationSettings.AppSettings["startId"];

            if (!int.TryParse(startId, out int id))
            {
                Console.WriteLine("StartIdKey is missing or not an integer !");
                Console.ReadKey();
            }

            Console.WriteLine("== Starting with id " + id);

            HttpClient client = new HttpClient();

            for (; id < int.MaxValue; id++)
            {
                try
                {
                    string url = string.Format(urlFormat, id);
                    var httpClient = new HttpClient();
                    var response = await httpClient.GetAsync(new Uri(url));

                    if (response.IsSuccessStatusCode)
                    {
                        var content = await response.Content.ReadAsStringAsync();
                        Console.WriteLine($"New page received for scrapping !");
                        try
                        {
                            Scrap(url, content);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("Error => " + ex.Message);
                        }
                    }
                    else
                    {
                        Console.Write($"/{id} not found (404)");
                    }
                }
                catch (Exception ex)
                {
                    Console.Write("Error => " + ex.Message);
                } 
            }
        }

        private HtmlNode GetNodeByClass(HtmlDocument document, string name)
        {
            return document
                  .DocumentNode
                  .Descendants()
                  .Where(x => x.Attributes.Contains("class") && x.Attributes["class"].Value.Contains(name)).FirstOrDefault();
        }
        private void Scrap(string url, string content)
        {
            HtmlDocument document = new HtmlDocument();
            document.LoadHtml(content);

            // Made it counter
            HtmlNode madeItNode = GetNodeByClass(document, "made-it-count");
            madeItNode = madeItNode.NextSibling;
            string madeItVal = madeItNode.InnerHtml;
            madeItVal = madeItVal.Replace("k", "000");
            madeItVal = madeItVal.Substring(0, madeItNode.InnerHtml.IndexOf("&"));
            int scrappedMadeItValNum = 0;

            if (int.TryParse(madeItVal, out int madeItValNum))
            {
                scrappedMadeItValNum = madeItValNum;
            }


            // Review counter 
            int scrappedReviewsValNum = 0;
            HtmlNode reviewNode = GetNodeByClass(document, "review-count");

            if (reviewNode != null)
            {
                string reviews = reviewNode.InnerHtml;
                reviews = reviews.Replace("k", "000");
                reviews = reviews.Replace("reviews", "").Trim();

                int reviewsIdx = reviews.IndexOf("&");

                if (reviewsIdx > 0)
                {
                    reviews = reviews.Substring(0, reviewsIdx);
                }

                if (int.TryParse(reviews, out int reviewsvalNum))
                {
                    scrappedReviewsValNum = reviewsvalNum;
                }
            }

            // Calories
            int scrappedCaloriesCount = 0;
            HtmlNode caloriesNode = GetNodeByClass(document, "calorie-count");
            if (caloriesNode != null)
            {
                caloriesNode = caloriesNode.FirstChild;
                int caloriesCount;

                string calories = caloriesNode.InnerText.Replace("k", "000");

                if (calories.IndexOf("&") > 0)
                {
                    calories = calories.Substring(0, calories.IndexOf("&"));
                }

                if (int.TryParse(calories, out caloriesCount))
                    scrappedCaloriesCount = caloriesCount;
            }

            // Rating
            int ratings = 0;
            HtmlNode ratingNodeContainer = GetNodeByClass(document, "rating-stars");
            if (ratingNodeContainer != null)
            {
                HtmlAttribute attrib = ratingNodeContainer.Attributes["data-ratingstars"];
                if (attrib != null)
                {
                    attrib.Value = attrib.Value.Replace("k", "000");

                    if (int.TryParse(attrib.Value, out int ratingVal))
                    {
                        ratings = ratingVal;
                    }
                }
            }

            // Servings
            int servings = 0;
            HtmlNode servingsNode = document.GetElementbyId("metaRecipeServings");
            if (servingsNode != null)
            {
                HtmlAttribute attrib = servingsNode.Attributes["content"];
                if (attrib != null)
                {
                    if (int.TryParse(attrib.Value, out int servingsVal))
                        servings = servingsVal;
                }
            }

            List<string> ingredients = new List<string>();

            // Ingredients
            HtmlNode ingredientsNode = document.GetElementbyId("polaris-app");
            if (ingredientsNode != null)
            {
                List<HtmlNode> ulNodes = ingredientsNode
                     .Descendants()
                     .Where(x => x.Name == "ul")
                     .ToList();

                foreach (HtmlNode ulNode in ulNodes)
                {
                    List<HtmlNode> nodes = ulNode
                        .Descendants()
                        .Where(x => x.Attributes["itemprop"] != null)
                        .ToList();

                    foreach (HtmlNode node in nodes)
                    {
                        ingredients.Add(node.InnerHtml);
                    }
                }
            }

            ScrappedPage spage = new ScrappedPage()
            {
                Url = url,
                Calories = scrappedCaloriesCount,
                NbOfPeopleWhoMadeId = scrappedMadeItValNum,
                Reviews = scrappedReviewsValNum,
                Servings = servings,
                Ingredients = ingredients.ToArray(),
                Stars = ratings
            };

            string encodedData = JsonConvert.SerializeObject(spage);
            Console.WriteLine(encodedData);

            using (StreamWriter w = File.AppendText("scrappedData.txt"))
            {
                w.WriteLine(encodedData + ",");
                w.Close();
            }

        }
    }
}
