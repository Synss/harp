import { Page } from "Components/Page"
import { OnQuerySuccess } from "Components/Utilities/OnQuerySuccess"
import { useDashboardDataQuery } from "Domain/Dashboard"
import { H2 } from "mkui/Components/Typography"

import { TransactionsOverviewChart, TransactionsOverview } from "./OverviewCharts"
import { EndpointChart } from "./EndpointChart"

export const OverviewPage = () => {
  const query = useDashboardDataQuery()
  const endpoints = ["foo", "bar"]

  return (
    <Page title="Overview" description="Useful insights">
      <OnQuerySuccess query={query} queries={[query, query]}>
        {(query) => {
          return <TransactionsOverviewChart data={query.data} title="Transactions Overview" />
        }}
      </OnQuerySuccess>

      {endpoints.map((endpoint, index) => (
        <TransactionsOverview key={index} endpoint={endpoint} title={endpoint} />
      ))}
    </Page>
  )
}
