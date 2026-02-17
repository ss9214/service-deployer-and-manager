import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { ExternalLink, RefreshCw, Trash2 } from 'lucide-react'

interface Service {
  id: number
  name: string
  repository_url: string
  repository_branch: string
  has_frontend: boolean
  has_backend: boolean
  has_database: boolean
  frontend_framework?: string
  backend_framework?: string
  database_type?: string
  frontend_url?: string
  backend_url?: string
  status: string
  estimated_monthly_cost?: number
  created_at: string
  last_deployed_at?: string
}

const fetchServices = async (): Promise<Service[]> => {
  const { data } = await axios.get('/api/services')
  return data
}

export default function Services() {
  const { data: services = [], isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: fetchServices,
  })

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Services</h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Deploy New Service
        </button>
      </div>

      {services.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg mb-4">
            No services deployed yet
          </p>
          <p className="text-gray-400 mb-6">
            Deploy your first service using the CLI:
          </p>
          <code className="block bg-gray-100 text-gray-800 px-4 py-2 rounded">
            deployer deploy https://github.com/username/repo
          </code>
        </div>
      ) : (
        <div className="grid gap-6">
          {services.map((service: Service) => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>
      )}
    </div>
  )
}

function ServiceCard({ service }: { service: Service }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {service.name}
          </h2>
          <a
            href={service.repository_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:underline flex items-center mt-1"
          >
            {service.repository_url}
            <ExternalLink className="w-3 h-3 ml-1" />
          </a>
        </div>
        <div className="flex gap-2">
          <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded">
            <RefreshCw className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded">
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <InfoItem label="Status" value={<StatusBadge status={service.status} />} />
        <InfoItem label="Branch" value={service.repository_branch} />
        <InfoItem
          label="Monthly Cost"
          value={`$${(service.estimated_monthly_cost || 0).toFixed(2)}`}
        />
        <InfoItem
          label="Last Deployed"
          value={
            service.last_deployed_at
              ? new Date(service.last_deployed_at).toLocaleDateString()
              : 'Never'
          }
        />
      </div>

      <div className="border-t pt-4">
        <div className="flex flex-wrap gap-2">
          {service.has_frontend && (
            <Badge color="blue">
              Frontend: {service.frontend_framework || 'Unknown'}
            </Badge>
          )}
          {service.has_backend && (
            <Badge color="green">
              Backend: {service.backend_framework || 'Unknown'}
            </Badge>
          )}
          {service.has_database && (
            <Badge color="purple">
              Database: {service.database_type || 'Unknown'}
            </Badge>
          )}
        </div>

        {(service.frontend_url || service.backend_url) && (
          <div className="mt-4 flex gap-4">
            {service.frontend_url && (
              <a
                href={service.frontend_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline flex items-center"
              >
                View Frontend
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            )}
            {service.backend_url && (
              <a
                href={service.backend_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline flex items-center"
              >
                View API
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-medium text-gray-900 mt-1">{value}</p>
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

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
  }

  return (
    <span
      className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${
        colorClasses[color as keyof typeof colorClasses]
      }`}
    >
      {children}
    </span>
  )
}
