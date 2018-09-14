using Scrapper.Services;
using System.Threading.Tasks;

namespace Scrapper
{
    class Program
    {
        static void Main(string[] args)
        {
            RecipeScrapper scrapper = new RecipeScrapper();
            scrapper.Run().Wait();
        }
    }
}
