<!-- "Next Steps" page copy. Edit the words; each block starts with @name. -->

@intro
Building a working machine-learning pipeline is a milestone, but data science gets truly useful when it leaves pure theory and reaches the community. This dashboard shows that demographic traits and visual patterns can offer real clues about shelter trends — but it's a beginning, not the end. From here the work splits into two related paths: growing the open data, and turning prediction into local advocacy.

@open_source
**Open data.** Our biggest limitation right now is that the model relies on static snapshots. Taiwan's Ministry of Agriculture open-data feed is volatile: when a dog is adopted, it simply disappears from the database. So the single most useful metric for evaluating a shelter — how many days an animal waited for a home — can't be recovered from one snapshot.

The fix is to turn our automated backend from a passive fetcher into a historical archive. By logging exactly when a unique animal ID appears and vanishes from the daily stream, we can build a dataset that connects tabular features to real waiting times. Published on Kaggle or Hugging Face, that preprocessed image-and-data set would give other researchers and future classes something structured to build on.

@website_outreach
**Website and outreach.** Our model is trained to spot quick adoptions — but it would be more useful to reverse that and lift the dogs facing the steepest climb. An "underdog" sort in the Discover feed, built by flipping the model's predicted probabilities, would push senior dogs, mixed breeds, and long-term residents to the top, giving the most exposure to the animals that need it most.

A data dashboard is also rarely where a family falls in love with a pet — that happens on social feeds like Instagram and LINE, or on bulletin boards in pet-friendly cafés and libraries. We want a friendlier interface and real outreach so the site reads as a place to discover dogs, not just a dataset host. A dedicated adoption app (we already have a wireframe) is one way to get there.

@closing
The hope is to show that machine learning doesn't have to be a cold, academic exercise. By pairing data engineering with local empathy, this project could grow from a capstone assignment into a living, public tool — a real bridge between Taiwan's shelters and the community.
