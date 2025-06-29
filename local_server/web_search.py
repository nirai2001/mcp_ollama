from langchain_community.tools import DuckDuckGoSearchResults
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("websearch", port=8002)

@mcp.tool()
def perform_search(query: str, limit: int = 1) -> list[str]:
    """
    Perform a web search using DuckDuckGo and return the top URLs.

    Args:
        query (str): The search query to be used.
        limit (int, optional): The maximum number of result URLs to return. Defaults to 1.

    Returns:
        list[str]: A list containing the top search result URLs.
    """
    search = DuckDuckGoSearchResults(output_format="list")
    search_results = search.invoke(query)
    urls = [item["link"] for item in search_results][:limit]
    return urls

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
  
