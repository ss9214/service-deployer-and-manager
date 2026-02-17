import React from 'react'

export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

      <div className="space-y-6">
        {/* AWS Configuration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            AWS Configuration
          </h2>
          <div className="space-y-4">
            <InfoRow label="Region" value="us-east-1" />
            <InfoRow label="VPC ID" value="vpc-xxxxx" />
            <InfoRow label="EC2 Instance" value="t3.medium" />
          </div>
        </div>

        {/* Vercel Configuration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Vercel Configuration
          </h2>
          <div className="space-y-4">
            <InfoRow label="Status" value="Connected" />
            <InfoRow label="Team" value="Personal Account" />
          </div>
        </div>

        {/* Platform Configuration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Platform Configuration
          </h2>
          <div className="space-y-4">
            <InfoRow label="Platform Name" value="My Deployment Platform" />
            <InfoRow label="Version" value="0.1.0" />
          </div>
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-3 border-b border-gray-200 last:border-0">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      <span className="text-sm text-gray-900">{value}</span>
    </div>
  )
}
