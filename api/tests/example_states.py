from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from geo_aval import DominanceGraph

keywords_chosen_state = {
   'messages': [
      HumanMessage(
         content='copapel',
         additional_kwargs={},
         response_metadata={},
         id='01715ac3-bbca-47cb-a12c-0126378e31a3'
      ),
      AIMessage(
         content=[
            {
               'type': 'text',
               'text': 'A Copapel é uma empresa brasileira especializada no fornecimento de soluções sustentáveis para higiene e limpeza profissional. Fundada em 1976 na cidade de Joinville, Santa Catarina, a Copapel se destaca como líder no setor de distribuição de produtos de higiene e limpeza no Sul do Brasil. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n**1. Visão Geral da Empresa**\n\n- **Modelo de Negócios**: A Copapel atua como distribuidora de produtos e serviços para higiene e limpeza profissional, oferecendo soluções sustentáveis e inovadoras para diversos segmentos de mercado. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n- **Setor da Indústria**: A empresa está inserida no setor de distribuição de produtos de higiene e limpeza, com foco em soluções sustentáveis e eficientes. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n**2. Produtos/Serviços**\n\n- **Ofertas Principais**: A Copapel oferece um portfólio diversificado com mais de 3.000 itens de fabricantes nacionais e internacionais, incluindo produtos como químicos concentrados, papel toalha, papel higiênico e soluções tecnológicas para otimização da gestão de compras e uso de insumos. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n- **Linhas de Produtos**: A empresa disponibiliza produtos para diversos segmentos, como centros de distribuição, lojas físicas e lavanderias, sempre com foco em qualidade, economia e sustentabilidade. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n**3. Mercado-Alvo**\n\n- **Segmentos de Clientes Primários**: A Copapel atende a uma ampla gama de clientes, incluindo grandes redes de supermercados, hospitais, clínicas, lavanderias e outros estabelecimentos que necessitam de soluções em higiene e limpeza profissional. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n- **Demografia**: A empresa possui unidades em Santa Catarina, Paraná e Rio Grande do Sul, atendendo a clientes em diversas regiões do Sul do Brasil. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai))\n\n**4. Proposta de Valor**\n\n- **Problemas Resolvidos**: A Copapel oferece soluções que permitem aos clientes economizar tempo, água, produtos químicos e custos com lavanderia, além de reduzir o descarte de plástico no meio ambiente. ([valoresdors.com.br](https://valoresdors.com.br/noticias/copapel-apresenta-solucoes-sustentaveis-no-health-meeting/?utm_source=openai))\n\n- **Pontos de Venda Únicos**: A empresa se destaca por integrar os princípios ESG (Ambiental, Social e Governança) em seu portfólio de soluções, promovendo a sustentabilidade e a eficiência nos processos de higiene e limpeza. ([copapel.com.br](https://copapel.com.br/blog/esg-e-sustentabilidade?utm_source=openai))\n\nCom mais de 47 anos de atuação, a Copapel continua a expandir sua presença no mercado, consolidando-se como uma referência em soluções sustentáveis para higiene e limpeza profissional no Brasil. ([copapel.com.br](https://copapel.com.br/institucional?utm_source=openai)) ',
               'annotations': [
                  {
                     'end_index': 365,
                     'start_index': 291,
                     'title': 'Copapel - Institucional',
                     'type': 'url_citation',
                     'url': 'https://copapel.com.br/institucional?utm_source=openai'
                  },
                  {
                     'end_index': 674,
                     'start_index': 600,
                     'title': 'Copapel - Institucional',
                     'type': 'url_citation',
                     'url': 'https://copapel.com.br/institucional?utm_source=openai'
                  },
                  {
                     'end_index': 907,
                     'start_index': 833,
                     'title': 'Copapel - Institucional',
                     'type': 'url_citation',
                     'url': 'https://copapel.com.br/institucional?utm_source=openai'
                  },
                  {
                     'end_index': 1303,
                     'start_index': 1229,
                     'title': 'Copapel - Institucional',
                     'type': 'url_citation',
                     'url': 'https://copapel.com.br/institucional?utm_source=openai'
                  },
                  {
                     'end_index': 1581,
                     'start_index': 1507,
                     'title': 'Copapel - Institucional',
      'type': 'url_citation',
      'url': 'https://copapel.com.br/institucional?utm_source=openai'
   },
   {
      'end_index': 1927,
      'start_index': 1853,
      'title': 'Copapel - Institucional',
      'type': 'url_citation',
      'url': 'https://copapel.com.br/institucional?utm_source=openai'
   },
   {
      'end_index': 2153,
      'start_index': 2079,
      'title': 'Copapel - Institucional',
      'type': 'url_citation',
      'url': 'https://copapel.com.br/institucional?utm_source=openai'
   },
   {
      'end_index': 2522,
      'start_index': 2386,
      'title': 'Copapel apresenta soluções sustentáveis no Health Meeting - Valores do RS',
      'type': 'url_citation',
      'url': 'https://valoresdors.com.br/noticias/copapel-apresenta-solucoes-sustentaveis-no-health-meeting/?utm_source=openai'
   },
   {
      'end_index': 2838,
      'start_index': 2750,
      'title': 'ESG e sustentabilidade: como transformar higiene e limpeza',
      'type': 'url_citation',
      'url': 'https://copapel.com.br/blog/esg-e-sustentabilidade?utm_source=openai'
   },
   {
      'end_index': 3109,
      'start_index': 3035,
      'title': 'Copapel - Institucional',
      'type': 'url_citation',
      'url': 'https://copapel.com.br/institucional?utm_source=openai'
   }
               ]
            }
         ],
         additional_kwargs={
            'tool_outputs': [
               {
   'id': 'ws_6868191eced0819cb016b3d4e4b7348908463547a95643d8',
   'action': {'query': 'Copapel empresa', 'type': 'search'},
   'status': 'completed',
   'type': 'web_search_call'
               }
            ]
         },
         response_metadata={
            'id': 'resp_6868191e5718819cb040ed788dcab2bd08463547a95643d8',
            'created_at': 1751652638.0,
            'metadata': {},
            'model': 'gpt-4.1-mini-2025-04-14',
            'object': 'response',
            'service_tier': 'default',
            'status': 'completed',
            'model_name': 'gpt-4.1-mini-2025-04-14'
         },
         id='msg_686819209cb8819c98d997ca7adc2b4a08463547a95643d8',
         usage_metadata={
            'input_tokens': 518,
            'output_tokens': 731,
            'total_tokens': 1249,
            'input_token_details': {'cache_read': 0},
            'output_token_details': {'reasoning': 0}
         }
      )
   ],
   'target': 'copapel',
   'location': 'joinville',
   'all_keywords': [
      'papel toalha para empresa',
      'onde comprar produtos de limpeza profissional',
      'produto para limpar banheiro industrial',
      'como economizar com produtos de higiene',
      'melhor papel higiênico para escritório',
      'fornecedor de material de limpeza em Joinville',
      'comprar produtos de limpeza sustentável',
      'empresa distribuidora papel toalha sul',
      'produtos de limpeza profissionais para clínicas',
      'produtos de higiene nível hospitalar',
      'sustentabilidade produtos de limpeza corporativo',
      'distribuidor de químicos concentrados',
      'fornecedores para lavanderia industrial SC',
      'limpeza eficiente supermercado',
      'fornecedor papel higiênico empresarial',
      'higienização profissional restaurantes',
      'soluções limpeza ecológica empresas',
      'papel toalha bobina preço',
      'empresa de higiene e limpeza perto de mim'
   ],
   'refined_keywords': [
      'papel toalha para empresa joinville',
      'onde comprar produtos de limpeza profissional joinville',
      'produto para limpar banheiro industrial joinville',
      'melhor papel higiênico para escritório joinville',
      'fornecedor de material de limpeza em Joinville joinville',
      'comprar produtos de limpeza sustentável joinville',
      'produtos de limpeza profissionais para clínicas joinville',
      'produtos de higiene nível hospitalar joinville',
      'fornecedores para lavanderia industrial SC joinville',
      'soluções limpeza ecológica empresas joinville'
   ],
   'graph': DominanceGraph(companies=[])
}