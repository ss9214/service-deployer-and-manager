import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Server, TrendingUp, DollarSign, Activity } from 'lucide-react'

interface Service {
  id: number
  name: string
  status: string
  estimated_monthly_cost: number
}

const fetchServices = async (): Promise<Service[]> => {
  const { data } = await axios.get('/api/services')
  return data
}

const fetchCostSummary = async () => {
  const { data } = await axios.get('/api/costs/summary')
  return data
}

export default function Dashboard() {
  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: fetchServices,
  })

  const { data: costSummary } = useQuery({
    queryKey: ['costSummary'],
    queryFn: fetchCostSummary,
  })

  const runningServices = services.filter((s: Service) => s.status === 'running').length
  const totalCost = costSummary?.total_monthly_cost || 0

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Services"
          value={services.length}
          icon={Server}
          color="blue"
        />
        <StatCard
          title="Running"
          value={runningServices}
          icon={Activity}
          color="green"
        />
        <StatCard
          title="Monthly Cost"
          value={`$${totalCost.toFixed(2)}`}
          icon={DollarSign}
          color="yellow"
        />
        <StatCard
          title="Deployments Today"
          value="0"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Recent Services */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Services
        </h2>
        {services.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No services deployed yet. Use the CLI to deploy your first service!
          </p>
        ) : (
          <div className="space-y-4">
            {services.slice(0, 5).map((service: Service) => (
              <div
                key={service.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div>
                  <h3 className="font-medium text-gray-900">{service.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Status: <StatusBadge status={service.status} />
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">Monthly Cost</p>
                  <p className="font-semibold text-gray-900">
                    ${(service.estimated_monthly_cost || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  color: 'blue' | 'green' | 'yellow' | 'purple'
}

function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const statusClasses = {
    running: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
    stopped: 'bg-gray-100 text-gray-800',
  }

  return (
    <span
      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
        statusClasses[status as keyof typeof statusClasses] || statusClasses.stopped
      }`}
    >
      {status}
    </span>
  )
}
