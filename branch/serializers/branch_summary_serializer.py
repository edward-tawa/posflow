from rest_framework import serializers
from branch.models.branch_model import Branch

class BranchSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']  # only the essential info
