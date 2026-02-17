import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { DollarSign } from 'lucide-react'

const fetchCostSummary = async () => {
  const { data } = await axios.get('/api/costs/summary')
  return data
}

export default function Costs() {
  const { data: costSummary, isLoading } = useQuery({
    queryKey: ['costSummary'],
    queryFn: fetchCostSummary,
  })

  if (isLoading) {
    return <div>Loading...</div>
  }

  const totalCost = costSummary?.total_monthly_cost || 0
  const services = costSummary?.services || []

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Cost Management</h1>

      {/* Total Cost Card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-8 mb-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-100 text-sm mb-2">
              Estimated Monthly Cost
            </p>
            <p className="text-5xl font-bold">${totalCost.toFixed(2)}</p>
            <p className="text-blue-100 text-sm mt-2">
              Across {costSummary?.num_services || 0} services
            </p>
          </div>
          <div className="bg-white/10 p-4 rounded-full">
            <DollarSign className="w-12 h-12" />
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Infrastructure Costs
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CostItem label="EC2 Compute" value="$30.37" percentage={60} />
          <CostItem label="RDS Database" value="$15.00" percentage={30} />
          <CostItem label="Data Transfer" value="$5.00" percentage={10} />
        </div>
      </div>

      {/* Service Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Cost by Service
        </h2>
        {services.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No services to display costs for
          </p>
        ) : (
          <div className="space-y-4">
            {services.map((service: { name: string; status: string; monthly_cost: number }, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div>
                  <h3 className="font-medium text-gray-900">{service.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Status: {service.status}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-semibold text-gray-900">
                    ${(service.monthly_cost || 0).toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-500">per month</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cost Optimization Tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          💡 Cost Optimization Tips
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Consider using smaller instance types for development services</li>
          <li>• Enable auto-scaling to match capacity with demand</li>
          <li>• Use RDS Reserved Instances for long-term deployments (up to 60% savings)</li>
          <li>• Review and remove unused services regularly</li>
        </ul>
      </div>
    </div>
  )
}

function CostItem({
  label,
  value,
  percentage,
}: {
  label: string
  value: string
  percentage: number
}) {
  return (
    <div>
      <div className="flex justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{percentage}% of total</p>
    </div>
  )
}
