"""
NEPSE Stock Database
50+ actively traded stocks on Nepal Stock Exchange.
Categorized by sector with real market data.
"""

NEPAL_STOCKS = [
    # ==========================================
    # COMMERCIAL BANKS (Class A) - 15 stocks
    # ==========================================
    {"symbol": "NABIL", "name": "Nabil Bank Limited", "sector": "Commercial Banks", "listed": "1984"},
    {"symbol": "NICA", "name": "NIC Asia Bank Limited", "sector": "Commercial Banks", "listed": "2004"},
    {"symbol": "GBIME", "name": "Global IME Bank Limited", "sector": "Commercial Banks", "listed": "2006"},
    {"symbol": "NIMB", "name": "Nepal Investment Mega Bank", "sector": "Commercial Banks", "listed": "2006"},
    {"symbol": "SCB", "name": "Standard Chartered Bank Nepal", "sector": "Commercial Banks", "listed": "1987"},
    {"symbol": "HBL", "name": "Himalayan Bank Limited", "sector": "Commercial Banks", "listed": "1993"},
    {"symbol": "EBL", "name": "Everest Bank Limited", "sector": "Commercial Banks", "listed": "1995"},
    {"symbol": "SANIMA", "name": "Sanima Bank Limited", "sector": "Commercial Banks", "listed": "2012"},
    {"symbol": "PRVU", "name": "Prabhu Bank Limited", "sector": "Commercial Banks", "listed": "2014"},
    {"symbol": "MBL", "name": "Machhapuchhre Bank Limited", "sector": "Commercial Banks", "listed": "2012"},
    {"symbol": "NBL", "name": "Nepal Bank Limited", "sector": "Commercial Banks", "listed": "1937"},
    {"symbol": "SBI", "name": "Nepal SBI Bank Limited", "sector": "Commercial Banks", "listed": "1994"},
    {"symbol": "LBL", "name": "Laxmi Sunrise Bank Limited", "sector": "Commercial Banks", "listed": "2010"},
    {"symbol": "KBL", "name": "Kumari Bank Limited", "sector": "Commercial Banks", "listed": "2011"},
    {"symbol": "CZBIL", "name": "Citizens Bank International", "sector": "Commercial Banks", "listed": "2013"},

    # ==========================================
    # DEVELOPMENT BANKS - 6 stocks
    # ==========================================
    {"symbol": "MNBBL", "name": "Muktinath Bikas Bank", "sector": "Development Banks", "listed": "2013"},
    {"symbol": "JBBL", "name": "Jyoti Bikas Bank", "sector": "Development Banks", "listed": "2010"},
    {"symbol": "SHINE", "name": "Shine Resunga Development Bank", "sector": "Development Banks", "listed": "2014"},
    {"symbol": "GRDBL", "name": "Green Development Bank", "sector": "Development Banks", "listed": "2015"},
    {"symbol": "SAPDBL", "name": "Saptakoshi Development Bank", "sector": "Development Banks", "listed": "2016"},
    {"symbol": "KSBBL", "name": "Kamana Sewa Bikas Bank", "sector": "Development Banks", "listed": "2012"},

    # ==========================================
    # FINANCE COMPANIES - 4 stocks
    # ==========================================
    {"symbol": "MFIL", "name": "Manjushree Finance Limited", "sector": "Finance", "listed": "2011"},
    {"symbol": "CFCL", "name": "Central Finance Company", "sector": "Finance", "listed": "2012"},
    {"symbol": "GMFIL", "name": "Guheshwori Merchant Bank", "sector": "Finance", "listed": "2013"},
    {"symbol": "ICFC", "name": "ICFC Finance Limited", "sector": "Finance", "listed": "2014"},

    # ==========================================
    # MICROFINANCE - 7 stocks
    # ==========================================
    {"symbol": "CBBL", "name": "Chhimek Laghubitta Bittiya Sanstha", "sector": "Microfinance", "listed": "2012"},
    {"symbol": "DDBL", "name": "Deprosc Laghubitta Bikas Bank", "sector": "Microfinance", "listed": "2013"},
    {"symbol": "SLBBL", "name": "Swabalamban Laghubitta", "sector": "Microfinance", "listed": "2014"},
    {"symbol": "NUBL", "name": "Nirdhan Utthan Laghubitta", "sector": "Microfinance", "listed": "2012"},
    {"symbol": "SABSL", "name": "Sadhana Laghubitta", "sector": "Microfinance", "listed": "2015"},
    {"symbol": "MLBBL", "name": "Mithila Laghubitta", "sector": "Microfinance", "listed": "2014"},
    {"symbol": "JALPA", "name": "Jalpa Samudayik Laghubitta", "sector": "Microfinance", "listed": "2016"},

    # ==========================================
    # HYDROPOWER - 10 stocks
    # ==========================================
    {"symbol": "CHCL", "name": "Chilime Hydropower Company", "sector": "Hydropower", "listed": "2011"},
    {"symbol": "API", "name": "Api Power Company", "sector": "Hydropower", "listed": "2013"},
    {"symbol": "AKPL", "name": "Arun Kabeli Power", "sector": "Hydropower", "listed": "2014"},
    {"symbol": "BPCL", "name": "Butwal Power Company", "sector": "Hydropower", "listed": "2010"},
    {"symbol": "NHPC", "name": "National Hydro Power", "sector": "Hydropower", "listed": "2010"},
    {"symbol": "UPPER", "name": "Upper Tamakoshi Hydropower", "sector": "Hydropower", "listed": "2019"},
    {"symbol": "SPHL", "name": "Sanima Mai Hydropower", "sector": "Hydropower", "listed": "2015"},
    {"symbol": "SHPC", "name": "Sanjen Hydropower Company", "sector": "Hydropower", "listed": "2016"},
    {"symbol": "RURU", "name": "Ruru Hydropower", "sector": "Hydropower", "listed": "2017"},
    {"symbol": "UNHPL", "name": "Union Hydropower", "sector": "Hydropower", "listed": "2018"},

    # ==========================================
    # LIFE INSURANCE - 5 stocks
    # ==========================================
    {"symbol": "NLIC", "name": "Nepal Life Insurance Company", "sector": "Life Insurance", "listed": "2012"},
    {"symbol": "LICN", "name": "Life Insurance Corporation Nepal", "sector": "Life Insurance", "listed": "2014"},
    {"symbol": "SLI", "name": "Surya Life Insurance", "sector": "Life Insurance", "listed": "2015"},
    {"symbol": "ALICL", "name": "Asian Life Insurance", "sector": "Life Insurance", "listed": "2016"},
    {"symbol": "NLICL", "name": "National Life Insurance", "sector": "Life Insurance", "listed": "2013"},

    # ==========================================
    # NON-LIFE INSURANCE - 5 stocks
    # ==========================================
    {"symbol": "NIL", "name": "Neco Insurance Limited", "sector": "Non-Life Insurance", "listed": "2013"},
    {"symbol": "SIC", "name": "Sagarmatha Insurance Company", "sector": "Non-Life Insurance", "listed": "2014"},
    {"symbol": "PRIN", "name": "Prabhu Insurance Limited", "sector": "Non-Life Insurance", "listed": "2015"},
    {"symbol": "IGI", "name": "IME General Insurance", "sector": "Non-Life Insurance", "listed": "2016"},
    {"symbol": "HEIC", "name": "Himalayan Everest Insurance", "sector": "Non-Life Insurance", "listed": "2017"},

    # ==========================================
    # INVESTMENT & INFRASTRUCTURE - 4 stocks
    # ==========================================
    {"symbol": "CIT", "name": "Citizen Investment Trust", "sector": "Investment", "listed": "2010"},
    {"symbol": "HIDCL", "name": "Hydroelectricity Investment & Development", "sector": "Investment", "listed": "2018"},
    {"symbol": "NIFRA", "name": "Nepal Infrastructure Bank", "sector": "Investment", "listed": "2020"},
    {"symbol": "NRN", "name": "NRN Infrastructure", "sector": "Investment", "listed": "2021"},

    # ==========================================
    # TELECOM & OTHERS - 3 stocks
    # ==========================================
    {"symbol": "NTC", "name": "Nepal Doorsanchar Company (Nepal Telecom)", "sector": "Telecom", "listed": "2010"},
    {"symbol": "SHIVM", "name": "Shivam Cements", "sector": "Manufacturing", "listed": "2018"},
    {"symbol": "UNL", "name": "Unilever Nepal Limited", "sector": "Manufacturing", "listed": "1992"},
]


# NEPSE Index
NEPSE_INDEX = {"symbol": "NEPSE", "name": "NEPSE Index", "sector": "Market Index"}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_all_stocks():
    """Return all NEPSE stocks."""
    return NEPAL_STOCKS

def get_all_symbols():
    """Return list of all stock symbols."""
    return [s['symbol'] for s in NEPAL_STOCKS]

def get_stock(symbol):
    """Get full info for a stock by symbol."""
    for s in NEPAL_STOCKS:
        if s['symbol'] == symbol.upper():
            return s
    return None

def get_sectors():
    """Get all unique sectors sorted alphabetically."""
    return sorted(list(set(s['sector'] for s in NEPAL_STOCKS)))

def get_stocks_by_sector(sector):
    """Filter stocks by sector."""
    if sector and sector != "All":
        return [s for s in NEPAL_STOCKS if s['sector'] == sector]
    return NEPAL_STOCKS

def search_stocks(query):
    """Search stocks by name or symbol."""
    q = query.lower()
    return [s for s in NEPAL_STOCKS if q in s['name'].lower() or q in s['symbol'].lower()]

def get_market_summary():
    """Get total market overview."""
    return {
        "total_stocks": len(NEPAL_STOCKS),
        "sectors": len(get_sectors()),
        "sector_list": get_sectors(),
        "stocks_by_sector": {s: len(get_stocks_by_sector(s)) for s in get_sectors()}
    }