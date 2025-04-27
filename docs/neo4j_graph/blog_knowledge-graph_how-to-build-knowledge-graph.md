The way we initially model our data when we start designing an application rarely resembles the model we end up with. Usually, our model changes as we understand the data better and our business asks different questions of the data.

When your database isn’t built to handle relationships, building an application and responding to change gets complicated. This points to what I call the “**data model problem**:” The physical model (how we actually store the data) doesn’t align well with the conceptual model (how we naturally think and talk about the data). For example, if you’re working with a relational database, you have to model all of your relationships using foreign keys and JOIN tables because relational databases (in an irony of nomenclature) don’t actually store relationships.

Because of this divergence between conceptual and physical models, our data becomes harder to use – the relationships and business rules get buried inside SQL queries and other code written by engineers and developers. [Knowledge graphs and graph databases](https://neo4j.com/whitepapers/developers-guide-how-to-build-knowledge-graph/) solve this dilemma by capturing relationships and business rules explicitly in the physical model itself. Relationships reside in the data structure of a graph database.

More in this guide:

* [What Is a Knowledge Graph?](#h-what-is-a-knowledge-graph)
* [Step 1: Define the Knowledge Graph Use Case](#h-step-1-define-the-knowledge-graph-use-case)
* + [RDF Triple Stores](#h-rdf-triple-stores)
  + [Property Graph Databases](#h-property-graph-databases)
* + [Create a Graph Data Model](#h-create-a-graph-data-model)
  + [Apply an Organizing Principle](#h-apply-an-organizing-principle)
* + [Gather Your Data](#h-gather-your-data)
  + [Clean Your Data](#h-clean-your-data)
* [Step 5: Ingest Data Into the Knowledge Graph](#h-step-5-ingest-data-into-the-knowledge-graph)
* + [Simple query testing](#h-simple-query-testing)
  + [Optimize the knowledge graph](#h-optimize-the-knowledge-graph)
* + [Evolve the Knowledge Graph](#h-evolve-the-knowledge-graph)
  + [Plan for the Future](#h-plan-for-the-future)
* [Conclusion: Why Build a Knowledge Graph?](#h-conclusion-why-build-a-knowledge-graph)

## **What Is a Knowledge Graph?**

A knowledge graph is a design pattern that organizes interrelated data entities and their semantic relationships. It is used to reason over data and surface insights, or *knowledge.*

[[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20240722075336/what-is-knowledge-graph-1024x536.png]](https://neo4j.com/whitepapers/developers-guide-how-to-build-knowledge-graph/)

You can think about a knowledge graph as a data layer that supports a [broad range of enterprise use cases](https://neo4j.com/use-cases/). It integrates with all types of data stores and typically comes into play when an organization requires a way to manage highly connected data.

A relational database has its uses, but a knowledge graph is much better suited for use cases that involve relationships. As our world (and, therefore, our data) becomes increasingly connected, these use cases are becoming increasingly common. Knowledge graphs, typically built on a graph database, have [flexible data structures that are optimized for relationships](https://neo4j.com/blog/what-is-knowledge-graph/).

A knowledge graph has three major components: **nodes** (the data entities), **relationships** between the nodes, and organizing principles. An **organizing principle** refers to the way you organize the data conceptually into categories, hierarchies, or other principles that are important to the use case.

A knowledge graph solves the data modeling problem by treating relationships as an integral component of data. Relationships are captured natively in the graph database rather than being reconstructed with code as JOINs.

## **Step 1: Define the Knowledge Graph Use Case**

Before diving into implementation, clearly define what problem your knowledge graph will solve. Knowledge graphs excel at organizing and querying complex data that, in a relational model, would require complex queries and often frequent changes. Some of the most common knowledge graph use cases include [recommendation engines](https://neo4j.com/use-cases/real-time-recommendation-engine/), [fraud detection](https://neo4j.com/use-cases/fraud-detection/) systems, [supply chain](https://neo4j.com/use-cases/supply-chain-management/) tracking, [GraphRAG](https://neo4j.com/blog/what-is-graphrag/) for enterprise search (a [generative AI](https://neo4j.com/generativeai/) usage), and [master data management](https://neo4j.com/use-cases/master-data-management/).

Choose a focused starting point rather than trying to model your entire domain upfront. For example, if you’re building an entity resolution system for customer data, you might start by modeling basic customer identifiers and their relationships (email, phone, address) before expanding to include transaction history, device IDs, and social connections. This lets you validate your approach with a manageable scope before expanding the model.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250312105015/fraud-detection-use-case-1-1024x559.png]

Knowledge graphs can be applied in a variety of domains. Some of my favorite examples involve massive amounts of data that, when analyzed in a knowledge graph, yield insights previously hidden (in columns and rows):

* [NASA](https://neo4j.com/case-studies/nasa/) connected decades of project data into a knowledge graph called “Lessons Learned Database.” The knowledge graph helped NASA’s engineers uncover trends and apply learnings to avoid repeating past mistakes, saving them over $2 million in the Mission to Mars.

* [Cisco](https://neo4j.com/case-studies/cisco/) created a metadata-driven knowledge graph to make 20 million internal documents easily searchable. The knowledge graph delivered accurate, context-rich content recommendations that helped Cisco close deals with customers faster, cutting search times in half and saving more than 4 million work hours annually.

* [Novartis](https://neo4j.com/case-studies/novartis/) built a biological knowledge graph that shows the relationships between genes, diseases, and compounds. By integrating phenotypic, historical, and medical research data, Novartis researchers can identify hidden relationships in biological systems, accelerating drug development timelines.

## **Step 2: Choose a Database Management System (Triple Store vs. Property Graph)**

The database management system (DBMS) you choose determines how you’ll model, query, and scale your knowledge graph over time. A DBMS that effectively supports the knowledge graph will allow you to address your use case and scale with the needs of the business.

[Triple stores and property graph databases](https://neo4j.com/blog/rdf-vs-property-graphs-knowledge-graphs/?utm_source=GSearch&utm_medium=PaidSearch&utm_campaign=Evergreen&utm_content=AMS-Search-SEMCE-DSA-None-SEM-SEM-NonABM&utm_term=&utm_adgroup=DSA&gad_source=1&gclid=Cj0KCQiAs5i8BhDmARIsAGE4xHyPeJTSAs8Z0v0IhZIdlYiofMBhEnDWUvIJakJUnAYdpQAV5bYIiYEaAr7iEALw_wcB) are two choices for building a knowledge graph. Property graphs are a popular, flexible option for building knowledge graphs, but you may have also heard of triple stores (sometimes called “RDF databases”).

### **RDF Triple Stores**

RDF (Resource Description Framework) databases, also called  “triple stores”, structure data as subject-predicate-object triples. Originally designed for the Semantic Web, triple stores remain useful for ontology management and metadata representation. However, their rigid structure poses challenges for modeling highly connected data.

To illustrate this: Say you want to add a new relationship between two entities and add some properties that describe the relationships. Because triple stores organize all data as groups of three (a triple), adding a new relationship will create a new triple (a unit that consists of three new entities), and each of the relationship’s properties will also be represented as another triple. This process is called reification.

Working with highly connected datasets in triple stores becomes complicated very quickly. The dataset tends to explode into many, many triples, which creates unnecessary complexity (and redundancy).

A  property graph model makes modeling easier and more intuitive because it supports data relationships natively (no reification is involved).

### **Property Graph Databases**

Property graph databases represent data as nodes (or entities), edges (the relationships between those entities), and properties (any additional information or description about a given node or relationship).

A graph database represents data as a network of entities without a prescribed data structure. The data model takes the form that you choose. For example, one part of the data model may have multiple relationships between entities, and another section of the data model may have one or none. The relationships between data entities exist in the database itself rather than in the code used to join tables (as you would do in a relational database). You can also create new relationships or add-on new datasets at any time without complicating the data model with extra entities (unlike triple store).

You can see the difference between a triple store (left) and a property graph model (right) by looking at a simple example of a sister who owns a car that both she and her brother drive:

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311194557/Triple-store-vs-property-graph-1024x427.png]

Triple store vs. property graph

In a property graph model, multiple relationships can exist between entities. You can add relationships or nodes at any time without changing the schema. In the steps below, you’ll learn how to build your graph data model from any dataset.

## **Step 3: Model the Knowledge Graph**

Graph data modeling is about how you represent your data as nodes and relationships. When you design your graph’s structure, you’re mapping out the best way to represent the domain.

You can create a free graph database instance in [Neo4j AuraDB](https://login.neo4j.com/u/signup/identifier?state=hKFo2SA4YXB2VkxUSjN1eWNZN25RbXZaRExfcjdteW4wUEd5WKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIExxUEYxb2V5OGU5amRVTGJ2c2RxZXJieUJyZWJmUDhFo2NpZNkgV1NMczYwNDdrT2pwVVNXODNnRFo0SnlZaElrNXpZVG8). Simply open an account (no credit card needed) and click the button “Create Instance”). Then, go to Data Importer to sketch out your graph data model.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311194649/auradb-instance.png]

### **Create a Graph Data Model**

Developing a graph data model involves identifying the key entities (nodes) and the relationships between them. You’ll start by analyzing your domain and defining the specific questions your application needs to answer. From there, you’ll determine the essential **nodes**, which represent the main objects in your dataset, such as customers, products, or transactions. The nodes will have one or more **Labels** that define the purpose, role, or type of the node.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311194832/define-nodes-1024x860.png]

Next, you’ll define **relationships** — the connections between nodes that capture how entities interact, like *purchased*, *follows*, *placed order,* or *belongs to*.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311194820/define-relationships-1024x328.png]

Then, you can add **properties,** which provide more detail about nodes and relationships. For example, a “Person” node could have properties like “first\_name” and “last\_name.”  The relationship “PLACED\_ORDER” might have properties such as “purchase\_date.”

To learn graph data modeling, I highly recommend the free, two-hour self-paced course [Graph Data Modeling Fundamentals](https://graphacademy.neo4j.com/courses/modeling-fundamentals/?ref=redirect/).

### **Apply an Organizing Principle**

An organizing principle creates a framework for the knowledge graph by embedding key business concepts or rules directly in the graph. Think of it as a flexible, conceptual structure that organizes your data so that the knowledge graph can deliver insights.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311194940/organizing-principle-1024x712.png]

An organizing principle can be as simple as a product taxonomy. A product taxonomy might group items into categories (e.g., Snacks, Fruit, Fresh Foods, and Fish) or hierarchies (e.g., Apple -> Fruit -> Food).

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311195014/foodstuffs-category-1024x500.png]

An organizing principle can be as complex as an ontology: a systematic mapping of data to a semantic network. An ontology standardizes how data is organized, classified, and interpreted, ensuring consistency across applications and systems.

While powerful, ontologies are complex and require significant effort to design and implement. For most projects, you can use simpler organizing principles and save ontologies for when you truly need them.

## **Step 4: Prepare Data for Ingestion**

Now that you’ve modeled the data structure, you can prepare the data that will populate your knowledge graph.

### **Gather Your Data**

Start by identifying the datasets relevant to your use case. These can include structured data (like tables or spreadsheets), semi-structured data (like JSON or XML files), and [unstructured data](https://neo4j.com/developer-blog/construct-knowledge-graphs-unstructured-text/) (like text documents, emails, or logs). In an ecommerce graph, for example, you’d include customer records, transaction histories, and product catalogs.

### **Clean Your Data**

Raw data can contain inconsistencies, errors, or missing values. Before loading the data into your knowledge graph, you’ll want to clean up the data. Data preparation tasks may include:

* **Standardizing Formats:** Verify that dates, numerical values, and text fields are consistent across all datasets.
* **Removing Duplicates:** Identify and merge duplicate records, such as multiple entries for the same customer or product. A graph data model can help you perform this “[entity resolution](https://neo4j.com/blog/graph-database/what-is-entity-resolution/)” step efficiently before you create the knowledge graph.
* **Handling Missing Values:** Decide how to address incomplete data, whether by imputing values, removing incomplete records, or flagging them for manual correction.
* **Correcting Errors:** Identify and fix inaccuracies, such as incorrect spellings, invalid IDs, or other inconsistencies.

## **Step 5: Ingest Data Into the Knowledge Graph**

Now that you’ve defined the graph data model, it’s time to ingest the data into a graph database instance. Under “Data services,” select “Import” and then connect your first data source. You can upload or drag CSV files into the data import service and map the elements in your data source to nodes, properties, and relationships in the graph.

This process can be iterative, but you’ll want to map each element (nodes and relationships in the graph data model) to your dataset. As each element is defined, Aura Workspace places a green check mark to show that the fields for the node or relationship were populated.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250311195225/ingest-data-1024x781.png]

During ingestion, start with a small sample to validate your graph structure and data mapping. Once confirmed, scale up to ingest the full datasets. Make sure that all the relevant datasets have been ingested correctly. Then, check the nodes, relationships, properties, and organizing principles in the graph to check that they’re mapped correctly to the graph data model.

Congratulations! You now have a knowledge graph.

## **Step 6: Test the Knowledge Graph**

Building your knowledge graph is a significant milestone, but the process isn’t complete until you’ve ensured it can answer the questions your use case needs to answer.

Testing the knowledge graph allows you to identify areas for improvement and optimize accordingly. Through this iterative process, you can confirm that your knowledge graph supports your use case and operates efficiently.

### **Simple query testing**

Run queries to check that the knowledge graph can answer your business questions. These queries should validate that the graph provides actionable insights and meets the goals you defined in Step 1.

In the ecommerce knowledge graph, for example, you can start with simple queries such as:

* What products has a specific customer purchased?
* What product categories have the highest volume of sales?
* What are the total sales for a product category over a specific period?

Then you can move on to more advanced queries such as:

* What products are frequently purchased together?
* What products should you recommend to a customer based on other customers with similar purchase histories?
* What product combinations drive repeat purchases and can be bundled to increase sales?

To learn how to use basic Cypher queries, get a free download of  [The Developer’s Guide: How to Build a Knowledge Graph](https://neo4j.com/whitepapers/developers-guide-how-to-build-knowledge-graph/).

### **Optimize the knowledge graph**

If your knowledge graph doesn’t deliver meaningful or expected results, you may need to revisit its foundations:

* **Review the Knowledge Graph Model (Step 3):** Assess whether the model truly represents your domain. Is there a better way to define nodes, relationships, properties, or organizing principles?

* **Identify Missing Data (Step 4):** Check if any datasets were excluded during data preparation or ingestion, or determine whether the knowledge graph needs additional datasets to provide better insights.

* **Validate Data (Step 5):** Ensure nodes, relationships, and properties were correctly transformed during ingestion and accurately represent the domain. For instance, verify that “Customers” are connected to their correct “Orders” or that “Product” nodes have complete properties associated with them.

## **Step 7: Maintain and Evolve Your Knowledge Graph**

You can adapt your knowledge graph to accommodate new data and business needs. In this way, the knowledge graph evolves over time to adapt to the inevitable changes that happen.

### **Evolve the Knowledge Graph**

Adapt the knowledge graph as your domain changes:

* **Add New Data Sources:** Enhance insights by integrating datasets like customer reviews.
* **Expand Use Cases:** Extend the graph to support new business needs, such as incorporating supplier networks in an e-commerce graph.
* **Refine the Model:** Continuously improve how relationships and concepts are structured as your understanding deepens.

### **Plan for the Future**

A knowledge graph should grow with the business. You can keep it scalable and efficient by applying best practices such as:

* **Automating Updates**: Use tools to streamline data ingestion, validation, and updates.
* **Monitoring Query Performance:** Regularly assess and optimize query execution as complexity increases.
* **Planning for Scalability**: Ensure your infrastructure can support larger datasets and evolving business needs.

Maintaining your knowledge graph ensures that you can keep delivering accurate insights as the business grows.

## **Conclusion: Why Build a Knowledge Graph?**

Traditional databases flatten rich relationships into rigid structures, while knowledge graphs let us represent data the way we naturally think about it: as a network of entities.

Organizations like NASA and Cisco use knowledge graphs to surface insights from highly connected data — insights that are difficult to detect in traditional relational systems. Common use cases for knowledge graphs include building recommendation engines, developing fraud detection systems, and using GraphRAG for enterprise search.

If you’re just getting started, it’s best to begin with a focus use case and follow the steps above for your proof of concept. Then, let your graph evolve as your needs and datasets change. Your first implementation doesn’t need to be perfect — just useful. As you gain experience and your knowledge graph matures, you’ll keep finding insights in connected data.

To build a knowledge graph proof of concept, pick up a free copy of [The Developer’s Guide: How to Build a Knowledge Graph](https://neo4j.com/whitepapers/developers-guide-how-to-build-knowledge-graph/). You’ll follow along our detailed walkthrough of a knowledge graph implementation with the Northwind dataset.

## The Developer’s Guide: How to Build a Knowledge Graph

This ebook gives you a step-by-step walkthrough on building your first knowledge graph.