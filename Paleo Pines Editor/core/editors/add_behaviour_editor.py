import copy


class AddBehaviourEditor:
    """
    Placeholder: UnityPy 1.25+ does NOT support adding new objects to an Environment.
    We can only clone/modify existing MonoBehaviours, not append new ones.
    """

    def __init__(self, bundle_loader, monoscripts):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts

    def clone_behaviour_in_place(self, source_name, new_name):
        env = self.bundle_loader.env
        if env is None:
            raise Exception("No bundle loaded.")

        src_obj = None
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                mb = obj.read()
                if getattr(mb, "m_Name", "") == source_name:
                    src_obj = obj
                    break

        if not src_obj:
            raise Exception(f"Source behaviour '{source_name}' not found.")

        tree = src_obj.read_typetree()
        tree["m_Name"] = new_name

        # IMPORTANT: this overwrites the same object – it does NOT create a new one
        src_obj.save_typetree(tree)
        return src_obj, tree

    def create_new_behaviour(self, *args, **kwargs):
        raise NotImplementedError(
            "Adding brand-new MonoBehaviours to a bundle is not supported by UnityPy's Environment API. "
            "You can only edit or repurpose existing ones."
        )
