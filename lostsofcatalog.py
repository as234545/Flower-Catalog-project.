from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, CatalogItem, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Aura M", email="mmq1114@gmail.com",
             picture='https://lh3.googleusercontent.com/a-/AAuE7mDzT5ws-XUJisun8vx5j5HsZqyUlUrzMWSztsyLEA=s192')
session.add(User1)
session.commit()

# Menu for UrbanBurger
Catalog1 = Catalog(user_id=1, name="Lilium")

session.add(Catalog1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Asiatic hybrids", description=" hybrids between species in Lilium section Sinomartagon.",
                           price="$7.50", family="Division I", catalog=Catalog1)

session.add(CatalogItem2)
session.commit()


CatalogItem1 = CatalogItem(user_id=1, name="Martagon hybrids", description="based on Lilium dalhansonii, ",
                           price="$2.99", family="Division II", catalog=Catalog1)

session.add(CatalogItem1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Candidum", description="mostly European species",
                           price="$5.50", family="Division III", catalog=Catalog1)

session.add(CatalogItem2)
session.commit()

CatalogItem3 = CatalogItem(user_id=1, name="American hybrids", description="originally derived from Lilium bolanderi",
                           price="$3.99", family="Division IV", catalog=Catalog1)

session.add(CatalogItem3)
session.commit()

CatalogItem4 = CatalogItem(user_id=1, name="Longiflorum hybrids",
                           description="cultivated forms of this species and its subspecies.", price="$7.99", family="Division V", catalog=Catalog1)

session.add(CatalogItem4)
session.commit()


# Menu for Super Stir Fry
Catalog2 = Catalog(user_id=1, name="Helianthus")

session.add(Catalog2)
session.commit()


CatalogItem1 = CatalogItem(user_id=1, name="Helianthus agrestis ",
                           description="It is found only in the states of Florida and Georgia in the southeastern United States.", price="$7.99", family=" Asteraceae", catalog=Catalog2)

session.add(CatalogItem1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Helianthus ambiguus",
                           description=" It is found only in the Great Lakes region of the United States", price="$25", family="Asteraceae", catalog=Catalog2)

session.add(CatalogItem2)
session.commit()

CatalogItem3 = CatalogItem(user_id=1, name="Helianthus angustifolius",
                           description="found in all the coastal states from Texas to Long Island,", price="15", family="Asteraceae", catalog=Catalog2)

session.add(CatalogItem3)
session.commit()


# Menu for Panda Garden
Catalog1 = Catalog(user_id=1, name="Rose")

session.add(Catalog1)
session.commit()


CatalogItem1 = CatalogItem(user_id=1, name="Ornamental plants",
                           description=" hybrids that were bred for their flowers", price="$8.99", family="Rosaceae", catalog=Catalog1)

session.add(CatalogItem1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Cut flowers", description=" Generally they are harvested and cut when in bud, ",
                           price="$6.99", family="Rosaceae", catalog=Catalog1)

session.add(CatalogItem2)
session.commit()

CatalogItem3 = CatalogItem(user_id=1, name="Perfume", description="Rose perfumes are made from rose oil ",
                           price="$9.95", family="Rosaceae", catalog=Catalog1)


# Menu for Thyme for that
Catalog1 = Catalog(user_id=1, name="Tulip")

session.add(Catalog1)
session.commit()


CatalogItem1 = CatalogItem(user_id=1, name="Tulipa orphanidea", description=" is a species of the Tulipa genus",
                           price="$2.99", family="   Liliaceae", catalog=Catalog1)

session.add(CatalogItem1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Tulipa clusiana",
                           description="It is widely cultivated as an ornamental and is reportedly naturalized in France,", price="$5.99", family="Liliaceae", catalog=Catalog1)

session.add(CatalogItem2)
session.commit()


# Menu for Tony's Bistro
Catalog1 = Catalog(user_id=1, name="Iris")

session.add(Catalog1)
session.commit()


CatalogItem1 = CatalogItem(user_id=1, name="Beardless rhizome iris",
                           description="Beardless rhizomatous iris types commonly found in the European garden are the Siberian iris (I. sibirica) and its hybrids,", price="$13.95", family="Iridaceae", catalog=Catalog1)

session.add(CatalogItem1)
session.commit()

CatalogItem2 = CatalogItem(user_id=1, name="Crested rhizome iris",
                           description="One specific species, Iris cristata from North America", price="$4.95", family="Iridaceae", catalog=Catalog1)

session.add(CatalogItem2)
session.commit()

CatalogItem3 = CatalogItem(user_id=1, name="Bulbing juno iris",
                           description=" this type of iris is one of the more popular bulb irises in cultivation.", price="$6.95", family="Iridaceae", catalog=Catalog1)

session.add(CatalogItem3)
session.commit()


print "added menu items!"
