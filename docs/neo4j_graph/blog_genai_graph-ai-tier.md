More in this guide:

* [Fragmented Data: The “Garbage In, Garbage Out” AI Challenge](#h-fragmented-data-the-garbage-in-garbage-out-ai-challenge)
* [The AI Tier: Why Agents Need Unified Knowledge](#h-the-ai-tier-why-agents-need-unified-knowledge)
* [Knowledge Graphs: The Data Layer for the AI Tier](#h-knowledge-graphs-the-data-layer-for-the-ai-tier)
* [GraphRAG: Ensuring Accurate, Contextual AI](#h-graphrag-ensuring-accurate-contextual-ai)
* [Graph Databases: Performance, Flexibility, and Deeper Insights](#h-graph-databases-performance-flexibility-and-deeper-insights)
* [Practical Steps to Unify SaaS Data for GenAI](#h-practical-steps-to-unify-saas-data-for-genai)

A social media post rarely generates the level of conversation I’ve witnessed last week. Klarna CEO Sebastian Siemiatkowski [shared](https://x.com/klarnaseb/status/1896698293759230429) how his company transformed its data architecture with Neo4j to support its GenAI initiatives, eliminating over 1,200 SaaS applications in the process. This topic has dominated virtually every meeting I’ve had since.

Sebastian touched on a challenge that every organization faces: traditional SaaS applications create fragmented data environments that don’t work for GenAI. Some conversations suggest that traditional SaaS is headed for extinction. It’s not. But we *are* witnessing the early stages of a fundamental shift in how enterprise software will be built and operated in an AI-driven future.

I’m seeing this shift firsthand at Neo4j. Companies succeeding with GenAI aren’t just adapting their existing systems. They’re completely rethinking how enterprise data should be structured. This post provides insights from Klarna’s journey on why connected data is essential for enterprise AI success and how it’s reshaping application architecture for an agentic future.

> Yes, we did shut down Salesforce a year ago, as we have many SaaS providers—an internal estimate is about 1,200 SaaS shut down.
>
> No, I don't think it is the end of Salesforce; might be the opposite.
>
> Here is what actually happened and how/why we originally intended to NOT share…
>
> — Sebastian Siemiatkowski (@klarnaseb) [March 3, 2025](https://twitter.com/klarnaseb/status/1896698293759230429?ref_src=twsrc%5Etfw)

  

## Fragmented Data: The “Garbage In, Garbage Out” AI Challenge

“Shit in, shit out,” [says Sebastian](https://x.com/klarnaseb/status/1896698293759230429): “The old universal truth of data scientists still holds true, even in AI.”

This truth is evident in almost every conversation I have with enterprise leaders. In fact, 85% of them cite data quality as their biggest obstacle to AI success. Even the most advanced large language models (LLMs) can’t overcome poor, disconnected, or contradictory data.

The problem isn’t so much bad data, but how fragmented it is. Most enterprises store information across hundreds of siloed systems, from CRMs and ERPs to project management tools and custom applications. Each maintains its own data model, unique concepts, and isolated context.

When AI attempts to navigate this fragmented landscape, it struggles to establish meaningful connections, similar to trying to understand a story by reading random paragraphs from different books. Sebastian put it perfectly: “Feeding an LLM the fractioned, fragmented, and dispersed world of corporate data will result in a very confused LLM.”

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250318051156/saas-intelligent-services-1024x436.png]

Business logic is shifting from being narrow and predefined within siloed applications to being applied dynamically by agents in the AI Tier, enabling adaptive cross-domain reasoning and intelligent services.

## The AI Tier: Why Agents Need Unified Knowledge

This fragmentation challenge coincides with a fundamental shift happening in enterprise software.

Microsoft CEO Satya Nadella [predicted](https://www.cxtoday.com/customer-data-platform/microsoft-ceo-ai-agents-will-transform-saas-as-we-know-it/) that traditional business applications will transform in the AI era, with logic shifting to an “AI tier” that operates across multiple data sources. No more rigid SaaS apps. AI agents instead will dynamically retrieve and process information across domains in real time, making enterprise software more adaptive and intelligent.

However, for this transformation to succeed, organizations are finding that they still need to solve the data fragmentation challenge. AI agents need more than direct access to data sources. They need a dynamic layer that connects knowledge across them.

Traditional data integration with its tabular ETL pipelines, warehouses, and predefined views doesn’t solve this problem. Traditional data integration was designed to answer known business questions. We’re now shifting from the rigid, predefined logic of the business application to autonomous agents that reason on the fly. The power of agentic reasoning is its adaptability: as a feature, it can’t be fully predicted in advance. It’s inherently complex, as agents must navigate and connect data across different domains. For agents to reason effectively in real time, they need to dynamically access information across data repositories and understand and interpret relationships within and across these repositories.

Relational data models struggle to provide the dynamic flexibility needed to represent interconnected data across business domains. They typically require either inefficient denormalization in large, flattened, monolithic tables or have to retain complex schemas for thousands of disparate normalized tables, making the data prohibitively challenging to navigate.

This is where a knowledge graph comes in. A knowledge graph enables dynamic flexibility by design, allowing AI to efficiently reason over complex, multi-domain relationships. Unlike rigid relational models, knowledge graphs provide an adaptive structure that seamlessly incorporates diverse entities and relationships. This flexibility makes them ideal for AI-driven systems, supporting dynamic retrieval, contextual understanding, and deeper insights across disparate data sources.

## Knowledge Graphs: The Data Layer for the AI Tier

When Klarna began their GenAI journey, they quickly realized that they needed to fundamentally rethink how their enterprise data was organized. Sebastian explains: “The utilization of SaaS to store all forms of knowledge of what Klarna is, why it exists, what it tries to accomplish, how it is doing… was fragmented over these SaaS systems – most of them having their own ideas and concepts and creating an unnavigable web of knowledge.” This fragmentation severely limited Klarna’s ability to build effective AI solutions that could deliver reliable, contextual responses.

A knowledge graph is a design pattern for organizing and accessing interrelated data. Knowledge graphs can be implemented in various ways, and property graph databases like Neo4j model them compactly as nodes connected by relationships, which can be further enriched with descriptive properties.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250318051654/property-graph-1-e1742300299830-1024x572.png]

A property graph illustrating how Neo4j’s data model represents information as nodes with properties connected by labeled, directional relationships. This structure preserves the natural connections in your data that AI systems need for accurate understanding and reasoning.

Graph makes data AI-ready in three essential ways:

1. **Context** **is embedded in the data** through relationships and properties allowing AI to traverse across information seamlessly.
2. **Knowledge grows and evolves naturally,** without disruptive schema changes, enabling new query patterns and data sources to be integrated quickly – gaining more value as connections increase.
3. **An organized data model (ontology) maintains standards,** ensuring AI systems work off a common vocabulary and consistent source of truth as they scale.

Equally important, knowledge graphs need the right database to deliver the performance required for real-time AI. It makes all the difference in how your knowledge graph performs, not just for the first use case but also for the ones that follow. This is why knowledge graphs are essential for the AI tier that Nadella described and that Klarna and other companies use. They create a connected data layer that maps fragmented information as a unified, contextual resource.

[Image failed to download: https://dist.neo4j.com/wp-content/uploads/20250318052001/knowledge-graph-essential-component.png]

Knowledge graphs are an essential component of the AI Tier to unify retrieval across data sources.

## GraphRAG: Ensuring Accurate, Contextual AI

Knowledge graphs create the foundation for AI-ready data. [GraphRAG](https://neo4j.com/blog/genai/what-is-graphrag/) is how AI systems access and use that knowledge.

GraphRAG combines graph traversals with semantic search to surface relevant portions of complex, domain-specific, and highly interconnected knowledge to LLMs. This makes GenAI applications more:

1. **Accurate**, gathering complete information from across relevant areas of the knowledge graph to correctly answer questions that involve multi-part logic;
2. **Explainable,** using explicit representations of knowledge to identify information and its sources in a human-readable way; and
3. **Governable,** by collecting real-time explainable metadata to help determine how best to use retrieved information given the user and prompt context.

Klarna’s AI assistant Kiki puts GraphRAG to work every day. By connecting their LLMs to a knowledge graph built on a Neo4j graph database, Klarna has created a system that quickly answers employee questions about organizational structure, processes, and resources.

“Kiki brings together information across multiple disparate and siloed systems, improves the quality of that information, and explores it,” Sebastian explained. This connected view of organizational knowledge has transformed how information flows. [Their results](https://neo4j.com/customer-stories/klarna/) have been remarkable:

* Kiki answers over 2,000 questions per day, with more than 250,000 employee queries processed since launch
* 85% of Klarna employees actively use the system
* Non-technical teams have adoption rates as high as 93% in some departments
* Response times for common queries dropped from minutes or hours to just seconds

The result, said Sebastian, “is having a huge impact on productivity in ways that were not possible to imagine before without graph and Neo4j.” Klarna’s implementation demonstrates how a graph database foundation can deliver transformative results when deployed at enterprise scale.

Klarna’s story has captured headlines, but they’re not alone in this transformation. Companies from [AbbVie](https://webinars.biorelate.com/jon-stevens-abbvie-inc-ask-arch) and [Pfizer](https://youtu.be/ER1dNDcJiXg) to [Virgin Media O2](https://uk.nttdata.com/insights/blog/augmented-software-architecture-a-moonshot-realised) and [Prospa](https://neo4j.com/customer-stories/prospa/) have demonstrated the value of GraphRAG in their organizations.

Take Prospa, Australia’s leading digital small business lender. They built a knowledge graph that connects all their lending data in a Neo4j graph database. Their team uses Microsoft Copilot to ask questions in plain English and get answers in minutes. “Anyone in our company can access deep insights without coding knowledge,” says Jin Foo, Prospa’s Head of Data & Analytics. Every answer is traceable to its source, giving executives the confidence they need for essential lending decisions.

**It’s having a huge impact on productivity in ways that were not possible to imagine before without graph and Neo4j.**

## Graph Databases: Performance, Flexibility, and Deeper Insights

Native graph databases offer unique and essential advantages for knowledge graphs experienced by Klarna and other companies:

* **Query Performance** for orders-of-magnitude faster multi-hop queries, as data is effectively pre-joined in nodes and relationships, significantly reducing time complexity. This ensures high query performance even as the dataset grows beyond billions of nodes, minimizing agent latency for real-time retrieval.
* **Flexible Data Modeling** enables agile development via a flexible schema that allows for dynamic nodes, relationships, and properties. This removes rigid database constraints while maintaining relationship structure, making it ideal for the iterative updates that knowledge graphs require. Developers also benefit from seamless integration of new data sources and modeling of complex, multi-domain relationships as AI-driven systems evolve.
* **Graph Data Science** unlocks and predicts deeper insights by applying 65+ ready-to-use advanced analytics and machine learning algorithms directly to connected data. Neo4j’s Graph Data Science library includes algorithms like PageRank for identifying influential nodes, community detection for revealing natural clusters, and pathfinding for optimizing routes and flows. These capabilities enable organizations to detect fraud patterns, predict future connections, personalize recommendations, and uncover hidden insights that traditional analytics often miss.

## Practical Steps to Unify SaaS Data for GenAI

Your data architecture determines what your AI can understand and accomplish. Traditional SaaS creates fragmented data, making it nearly impossible for AI to establish needed context and connections.

The good news is that you don’t need to redesign everything to start seeing value. Graph databases enable incremental AI modernization, integrating alongside existing systems and allowing you to expand over time.

**Step 1: Identify a business application to modernize**

Begin in a low-risk, high-value area – somewhere you can deliver impact quickly without disrupting core operations. For example, an internal knowledge assistant, where AI can retrieve information from wikis, project management tools, and collaboration platforms to improve response accuracy.

**Step 2: Build a Knowledge Graph to break down data silos**

You don’t need to migrate all your data. Start with a knowledge graph as an abstraction layer on top of your existing SaaS data that models how AI should access, use, and connect information. Even starting with a simple metadata graph (datasets, schemas, owners, context, relationships) provides massive gains.

**Step 3: Create agentic workflows with GraphRAG**

Use the knowledge graph to guide how AI agents retrieve and reason over enterprise knowledge. This improves accuracy, explainability, and real-time contextual responses while enabling AI to orchestrate workflows across previously siloed data.

**Step 4: Expand Incrementally, consolidating applications**

Once the initial use case succeeds, assess your traditional SaaS application portfolio for consolidation and identify adjacent applications that could benefit from AI-driven workflows.

For example, if you start with a customer knowledge assistant that replaces your customer service SaaS application, you could extend it to finance and transaction systems next, creating a connected view across customer relationships and financial activities. From there, a natural progression would be integrating your product data, allowing your AI agents to reason across customers, transactions, and products for deeper insights and more informed business decisions.

The beauty of graph-based architectures is that once you set up the knowledge graph, you can incrementally consolidate business applications into the AI tier, allowing for more context-aware adaptive experiences.

Here are resources to help you get started below:

* [**The GraphRAG Manifesto:**](https://neo4j.com/blog/genai/graphrag-manifesto/) Discover why combining knowledge graphs with retrieval-augmented generation enables accurate, explainable AI
* [**Knowledge Graph Builder:**](https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/) Quickly build and experiment with knowledge graphs
* [**GraphAcademy:**](https://graphacademy.neo4j.com/categories/) Learn the [basics of a graph database](https://graphacademy.neo4j.com/courses/neo4j-fundamentals/?category=start), [graph modeling](https://graphacademy.neo4j.com/courses/modeling-fundamentals/?category=start), and [GraphRAG](https://graphacademy.neo4j.com/courses/llm-fundamentals/?category=generative-ai)
* [**Get to Know Graph Webinars:**](https://neo4j.com/events/get-to-know-graph/) Join these 30-minute sessions to learn how knowledge graphs improve AI responses
* [**Join the Graph Community:**](https://neo4j.com/events/) Attend a meetup or an event near you

---

¹ [*KPMG AI Quarterly Pulse Survey: High hopes, high hurdles, and the pursuit of realizing value*](https://view.ceros.com/kpmg-design/kpmg-genai-study/p/1)*, 2025.*