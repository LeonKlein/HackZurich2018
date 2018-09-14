namespace Scrapper.Models
{
    class ScrappedPage
    {
        public string Url { get; set; }
        public int Servings { get; set; }
        public int Calories { get; set; }
        public int Stars { get; set; }
        public string[] Ingredients { get; set; }
        public int Reviews { get; set; }
        public int NbOfPeopleWhoMadeId { get; set; }
    }
}
