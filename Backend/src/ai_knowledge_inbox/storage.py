from typing import List, Dict, Any, Optional

class InMemoryStore:
    """
    In-memory storage for items (notes/URLs) and embedded chunks.
    Provides methods for CRUD operations and retrieval.
    """
    def __init__(self):
        # Items stored by UUID: { "uuid-string": { ...item_data } }
        self.items: Dict[str, Dict[str, Any]] = {}
        # List of all chunk objects with embeddings
        self.chunks: List[Dict[str, Any]] = []

    def add_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new item to memory"""
        self.items[item["id"]] = item
        return item

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Return all items sorted by newest first"""
        items_list = list(self.items.values())
        return sorted(items_list, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Find an item by its ID"""
        return self.items.get(item_id)

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        """Append searchable chunk vectors"""
        self.chunks.extend(new_chunks)

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all searchable chunks"""
        return self.chunks

    def clear(self):
        """Clear memory (useful for testing)"""
        self.items.clear()
        self.chunks.clear()

# Shared singleton instance
store = InMemoryStore()
