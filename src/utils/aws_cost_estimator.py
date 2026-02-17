"""AWS cost estimation utilities."""

from typing import Optional
from ..config.schemas import CostEstimate, DatabaseType


class AWSCostEstimator:
    """Estimates AWS costs for deployments."""

    # Pricing as of 2026 for us-east-1 (prices in USD/month)
    EC2_PRICING = {
        "t3.micro": 7.59,
        "t3.small": 15.18,
        "t3.medium": 30.37,
        "t3.large": 60.74,
        "t3.xlarge": 121.47,
    }

    RDS_PRICING = {
        "db.t3.micro": 12.78,
        "db.t3.small": 25.55,
        "db.t3.medium": 51.10,
        "db.t4g.micro": 10.95,
        "db.t4g.small": 21.90,
        "db.t4g.medium": 43.80,
    }

    # Storage pricing (per GB/month)
    EBS_STORAGE_PRICE = 0.10  # General Purpose SSD (gp3)
    RDS_STORAGE_PRICE = 0.115  # General Purpose SSD (gp2)

    # Data transfer pricing (per GB)
    DATA_TRANSFER_OUT = 0.09  # First 10TB/month

    def __init__(self) -> None:
        """Initialize cost estimator."""
        pass

    def estimate_deployment_cost(
        self,
        ec2_instance_type: str = "t3.medium",
        has_database: bool = False,
        database_type: Optional[DatabaseType] = None,
        database_instance_type: str = "db.t3.micro",
        database_storage_gb: int = 20,
        estimated_monthly_data_transfer_gb: int = 50,
        num_deployments: int = 1,
    ) -> CostEstimate:
        """
        Estimate monthly AWS costs for a deployment.

        Args:
            ec2_instance_type: EC2 instance type for Kubernetes cluster
            has_database: Whether a database is needed
            database_type: Type of database (postgres, mysql, etc.)
            database_instance_type: RDS instance type
            database_storage_gb: Database storage in GB
            estimated_monthly_data_transfer_gb: Estimated data transfer per month
            num_deployments: Number of services deployed on the infrastructure

        Returns:
            CostEstimate object with breakdown
        """
        notes = []

        # EC2 costs
        ec2_monthly = self.EC2_PRICING.get(ec2_instance_type, 30.37)
        notes.append(f"EC2 {ec2_instance_type} instance for Kubernetes cluster")

        # Add EBS storage for EC2 (assume 30GB)
        ebs_storage_cost = 30 * self.EBS_STORAGE_PRICE
        ec2_monthly += ebs_storage_cost
        notes.append("30GB EBS storage for EC2 instance")

        # RDS costs
        rds_monthly = 0.0
        if has_database:
            rds_monthly = self.RDS_PRICING.get(database_instance_type, 12.78)
            rds_storage_cost = database_storage_gb * self.RDS_STORAGE_PRICE
            rds_monthly += rds_storage_cost

            db_type_name = database_type.value if database_type else "database"
            notes.append(f"RDS {database_instance_type} for {db_type_name}")
            notes.append(f"{database_storage_gb}GB RDS storage")

        # Data transfer costs
        data_transfer_monthly = estimated_monthly_data_transfer_gb * self.DATA_TRANSFER_OUT
        notes.append(f"~{estimated_monthly_data_transfer_gb}GB data transfer per month")

        # Total
        total_monthly = ec2_monthly + rds_monthly + data_transfer_monthly

        notes.append(f"Infrastructure shared across {num_deployments} service(s)")

        if num_deployments == 0:
            notes.append("Note: Costs shown are for baseline infrastructure")
        else:
            notes.append(
                f"Cost per service: ${total_monthly / num_deployments:.2f}/month"
            )

        return CostEstimate(
            ec2_monthly=round(ec2_monthly, 2),
            rds_monthly=round(rds_monthly, 2),
            data_transfer_monthly=round(data_transfer_monthly, 2),
            total_monthly=round(total_monthly, 2),
            currency="USD",
            notes=notes,
        )

    def estimate_new_database_cost(
        self,
        database_type: DatabaseType,
        instance_type: str = "db.t3.micro",
        storage_gb: int = 20,
    ) -> float:
        """
        Estimate the additional monthly cost for adding a new database.

        Args:
            database_type: Type of database
            instance_type: RDS instance type
            storage_gb: Storage in GB

        Returns:
            Monthly cost in USD
        """
        instance_cost = self.RDS_PRICING.get(instance_type, 12.78)
        storage_cost = storage_gb * self.RDS_STORAGE_PRICE
        return round(instance_cost + storage_cost, 2)

    def get_recommended_instance_sizes(
        self, num_services: int, expected_traffic: str = "low"
    ) -> dict[str, str]:
        """
        Get recommended instance sizes based on number of services and traffic.

        Args:
            num_services: Number of services to deploy
            expected_traffic: Traffic level (low, medium, high)

        Returns:
            Dictionary with ec2_instance and db_instance recommendations
        """
        recommendations = {}

        # EC2 recommendations
        if expected_traffic == "high" or num_services > 5:
            recommendations["ec2_instance"] = "t3.large"
        elif expected_traffic == "medium" or num_services > 2:
            recommendations["ec2_instance"] = "t3.medium"
        else:
            recommendations["ec2_instance"] = "t3.small"

        # Database recommendations
        if expected_traffic == "high":
            recommendations["db_instance"] = "db.t3.medium"
        elif expected_traffic == "medium":
            recommendations["db_instance"] = "db.t3.small"
        else:
            recommendations["db_instance"] = "db.t3.micro"

        return recommendations

    def compare_instance_types(self, instance_family: str = "ec2") -> dict[str, float]:
        """
        Get pricing comparison for different instance types.

        Args:
            instance_family: 'ec2' or 'rds'

        Returns:
            Dictionary mapping instance types to monthly costs
        """
        if instance_family == "ec2":
            return self.EC2_PRICING.copy()
        elif instance_family == "rds":
            return self.RDS_PRICING.copy()
        else:
            return {}
